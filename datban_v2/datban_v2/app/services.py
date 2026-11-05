"""TẦNG NGHIỆP VỤ - toàn bộ business rules nằm ở đây (không phụ thuộc Flask).
Mỗi hàm tương ứng một use-case trong tài liệu đặc tả (ghi chú UCxx)."""
import re
import secrets
import string
from datetime import datetime, timedelta

from mysql.connector import errors as dberr
from werkzeug.security import check_password_hash, generate_password_hash

from . import config as C
from .db import execute, execute_many, query, transaction

ACTIVE = "('DA_XAC_NHAN','DA_CHECK_IN')"      # các trạng thái đang giữ bàn


class BookingError(Exception):
    """Lỗi vi phạm business rule - thông điệp hiển thị trực tiếp cho người dùng."""


# ============================== tiện ích nội bộ ==============================
def _gen_code(conn):
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = "".join(secrets.choice(alphabet) for _ in range(8))
        if not query(conn, "SELECT 1 FROM dat_ban WHERE ma_xac_nhan=%s", (code,), one=True):
            return code
    raise BookingError("Không tạo được mã xác nhận, vui lòng thử lại")


def _log(conn, ma_dat_ban, action, detail="", staff_id=None):
    execute(conn, "INSERT INTO nhat_ky_dat_ban (ma_dat_ban, ma_nhan_vien, hanh_dong, chi_tiet) VALUES (%s,%s,%s,%s)",
            (ma_dat_ban, staff_id, action, detail))


def _validate_time(start, party, now):
    end = start + timedelta(minutes=C.DURATION_MIN)
    if not 1 <= party <= C.MAX_PARTY:                                           # BR05
        raise BookingError(f"Số người phải từ 1 đến {C.MAX_PARTY}")
    if start < now + timedelta(minutes=C.MIN_ADVANCE_MIN):                      # BR04
        raise BookingError(f"Phải đặt trước ít nhất {C.MIN_ADVANCE_MIN} phút")
    if start > now + timedelta(days=C.MAX_ADVANCE_DAYS):
        raise BookingError(f"Chỉ nhận đặt trước tối đa {C.MAX_ADVANCE_DAYS} ngày")
    open_t = start.replace(hour=C.OPEN_HOUR, minute=0, second=0, microsecond=0)
    close_t = start.replace(hour=C.CLOSE_HOUR, minute=0, second=0, microsecond=0)
    if start < open_t or end > close_t:                                         # BR01, BR02
        raise BookingError(f"Nhà hàng mở {C.OPEN_HOUR}:00-{C.CLOSE_HOUR}:00; lượt đặt kéo dài {C.DURATION_MIN} phút "
                           f"nên giờ đến muộn nhất là {(close_t - timedelta(minutes=C.DURATION_MIN)):%H:%M}")
    return end


def _validate_customer(ho_ten, sdt):
    if not ho_ten or not ho_ten.strip():
        raise BookingError("Họ tên không được để trống")
    if not re.fullmatch(r"0\d{9,10}", sdt or ""):                               # BR08
        raise BookingError("Số điện thoại không hợp lệ (10-11 số, bắt đầu bằng 0)")


def _conflict(conn, ma_ban, start, end, exclude_id=None):                       # BR03
    sql = (f"SELECT ma_dat_ban FROM dat_ban WHERE ma_ban=%s AND trang_thai IN {ACTIVE} "
           "AND thoi_gian_bat_dau < %s AND thoi_gian_ket_thuc > %s")
    params = [ma_ban, end + timedelta(minutes=C.BUFFER_MIN), start - timedelta(minutes=C.BUFFER_MIN)]
    if exclude_id:
        sql += " AND ma_dat_ban <> %s"
        params.append(exclude_id)
    return query(conn, sql + " LIMIT 1", params, one=True) is not None


# ============================== UC01 Tra cứu bàn trống ==============================
def find_available_tables(conn, start, party, area_id=None, exclude_id=None):
    """Bàn trống phù hợp, sắp theo sức chứa tăng dần (bàn vừa nhất đứng đầu) - BR05, BR09."""
    end = start + timedelta(minutes=C.DURATION_MIN)
    sql = ("SELECT b.ma_ban, b.ten_ban, b.suc_chua, kv.ten_khu_vuc, b.ma_khu_vuc "
           "FROM ban b JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc WHERE b.bao_tri=0 AND b.suc_chua>=%s")
    params = [party]
    if area_id:
        sql += " AND b.ma_khu_vuc=%s"
        params.append(int(area_id))
    sql += (f" AND NOT EXISTS (SELECT 1 FROM dat_ban d WHERE d.ma_ban=b.ma_ban AND d.trang_thai IN {ACTIVE} "
            "AND d.thoi_gian_bat_dau < %s AND d.thoi_gian_ket_thuc > %s")
    params += [end + timedelta(minutes=C.BUFFER_MIN), start - timedelta(minutes=C.BUFFER_MIN)]
    if exclude_id:
        sql += " AND d.ma_dat_ban <> %s"
        params.append(exclude_id)
    return query(conn, sql + ") ORDER BY b.suc_chua, b.ten_ban", params)


def list_areas(conn):
    return query(conn, "SELECT * FROM khu_vuc ORDER BY ma_khu_vuc")


# ============================== UC02 Đặt bàn ==============================
def create_reservation(conn, ho_ten, sdt, start, party, email=None, ma_ban=None,
                       area_id=None, ghi_chu=None, now=None):
    now = now or datetime.now()
    _validate_customer(ho_ten, sdt)
    end = _validate_time(start, party, now)
    with transaction(conn):
        candidates = [int(ma_ban)] if ma_ban else [t["ma_ban"] for t in find_available_tables(conn, start, party, area_id)]
        chosen = None
        for tid in candidates:
            ban = query(conn, "SELECT * FROM ban WHERE ma_ban=%s FOR UPDATE", (tid,), one=True)   # khóa dòng chống đặt trùng
            if not ban or ban["bao_tri"] or ban["suc_chua"] < party:
                if ma_ban:
                    raise BookingError("Bàn đã chọn không phù hợp (đang bảo trì hoặc không đủ chỗ)")
                continue
            if not _conflict(conn, tid, start, end):
                chosen = ban
                break
            if ma_ban:
                raise BookingError("Bàn đã chọn đã có người đặt trong khung giờ này")
        if not chosen:
            raise BookingError("Hết bàn trống phù hợp trong khung giờ này, vui lòng chọn giờ khác")
        kh = query(conn, "SELECT ma_khach FROM khach_hang WHERE so_dien_thoai=%s", (sdt,), one=True)
        if kh:
            ma_khach = kh["ma_khach"]
            execute(conn, "UPDATE khach_hang SET ho_ten=%s, email=COALESCE(%s,email) WHERE ma_khach=%s",
                    (ho_ten.strip(), email, ma_khach))
        else:
            ma_khach = execute(conn, "INSERT INTO khach_hang (ho_ten, so_dien_thoai, email) VALUES (%s,%s,%s)",
                               (ho_ten.strip(), sdt, email))
        code = _gen_code(conn)
        rid = execute(conn, "INSERT INTO dat_ban (ma_xac_nhan, ma_khach, ma_ban, thoi_gian_bat_dau, thoi_gian_ket_thuc, "
                            "so_nguoi, ghi_chu) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                      (code, ma_khach, chosen["ma_ban"], start, end, party, ghi_chu))
        _log(conn, rid, "TAO", f"Bàn {chosen['ten_ban']}, {party} người")
    return get_reservation(conn, code)


# ============================== UC03 Tra cứu lượt đặt ==============================
def get_reservation(conn, code):
    r = query(conn,
              "SELECT d.*, b.ten_ban, b.suc_chua, kv.ten_khu_vuc, k.ho_ten, k.so_dien_thoai, k.email "
              "FROM dat_ban d JOIN ban b ON b.ma_ban=d.ma_ban JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc "
              "JOIN khach_hang k ON k.ma_khach=d.ma_khach WHERE d.ma_xac_nhan=%s", ((code or "").upper().strip(),), one=True)
    if not r:
        raise BookingError("Không tìm thấy mã đặt bàn")
    return r


def find_by_phone(conn, sdt):
    return query(conn,
                 "SELECT d.ma_xac_nhan, d.thoi_gian_bat_dau, d.so_nguoi, d.trang_thai, b.ten_ban "
                 "FROM dat_ban d JOIN ban b ON b.ma_ban=d.ma_ban JOIN khach_hang k ON k.ma_khach=d.ma_khach "
                 "WHERE k.so_dien_thoai=%s ORDER BY d.thoi_gian_bat_dau DESC LIMIT 50", (sdt,))


# ============================== UC04 Đổi lịch / UC05 Hủy ==============================
def _require_changeable(r, now):                                                # BR06
    if r["trang_thai"] != "DA_XAC_NHAN":
        raise BookingError("Chỉ đổi/hủy được lượt đặt đang ở trạng thái 'Đã xác nhận'")
    if now > r["thoi_gian_bat_dau"] - timedelta(minutes=C.CANCEL_BEFORE_MIN):
        raise BookingError(f"Chỉ được đổi/hủy trước giờ đặt ít nhất {C.CANCEL_BEFORE_MIN // 60} giờ")


def cancel_reservation(conn, code, now=None):
    now = now or datetime.now()
    r = get_reservation(conn, code)
    _require_changeable(r, now)
    execute(conn, "UPDATE dat_ban SET trang_thai='DA_HUY' WHERE ma_dat_ban=%s", (r["ma_dat_ban"],))
    _log(conn, r["ma_dat_ban"], "HUY")
    return get_reservation(conn, code)


def modify_reservation(conn, code, new_start=None, new_party=None, now=None):
    """Đổi giờ / số người. Giữ bàn cũ nếu còn phù hợp, nếu không tự bố trí bàn khác."""
    now = now or datetime.now()
    r = get_reservation(conn, code)
    _require_changeable(r, now)
    start = new_start or r["thoi_gian_bat_dau"]
    party = new_party or r["so_nguoi"]
    end = _validate_time(start, party, now)
    with transaction(conn):
        keep = query(conn, "SELECT * FROM ban WHERE ma_ban=%s FOR UPDATE", (r["ma_ban"],), one=True)
        if keep["suc_chua"] >= party and not keep["bao_tri"] and not _conflict(conn, keep["ma_ban"], start, end, r["ma_dat_ban"]):
            ma_ban = keep["ma_ban"]
        else:
            options = find_available_tables(conn, start, party, exclude_id=r["ma_dat_ban"])
            if not options:
                raise BookingError("Không còn bàn phù hợp với thay đổi này")
            ma_ban = options[0]["ma_ban"]
        execute(conn, "UPDATE dat_ban SET thoi_gian_bat_dau=%s, thoi_gian_ket_thuc=%s, so_nguoi=%s, ma_ban=%s "
                      "WHERE ma_dat_ban=%s", (start, end, party, ma_ban, r["ma_dat_ban"]))
        _log(conn, r["ma_dat_ban"], "DOI", f"{start:%d/%m %H:%M}, {party} người")
    return get_reservation(conn, code)


# ============================== UC08 Check-in / UC09 Hoàn thành / UC11 Vắng mặt ==============================
def check_in(conn, code, now=None, staff_id=None):
    now = now or datetime.now()
    r = get_reservation(conn, code)
    if r["trang_thai"] != "DA_XAC_NHAN":
        raise BookingError(f"Không thể check-in: lượt đặt đang ở trạng thái {r['trang_thai']}")
    earliest = r["thoi_gian_bat_dau"] - timedelta(minutes=C.CHECKIN_EARLY_MIN)  # BR07
    latest = r["thoi_gian_bat_dau"] + timedelta(minutes=C.CHECKIN_LATE_MIN)
    if now < earliest:
        raise BookingError(f"Chưa đến giờ check-in (từ {earliest:%H:%M})")
    if now > latest:
        raise BookingError(f"Đã quá hạn check-in ({latest:%H:%M}); lượt đặt sẽ bị đánh dấu vắng mặt")
    execute(conn, "UPDATE dat_ban SET trang_thai='DA_CHECK_IN', gio_check_in=%s WHERE ma_dat_ban=%s", (now, r["ma_dat_ban"]))
    _log(conn, r["ma_dat_ban"], "CHECK_IN", staff_id=staff_id)
    return get_reservation(conn, code)


def complete(conn, code, staff_id=None):
    r = get_reservation(conn, code)
    if r["trang_thai"] != "DA_CHECK_IN":
        raise BookingError("Chỉ hoàn thành được lượt đặt đã check-in")
    execute(conn, "UPDATE dat_ban SET trang_thai='HOAN_THANH' WHERE ma_dat_ban=%s", (r["ma_dat_ban"],))
    _log(conn, r["ma_dat_ban"], "HOAN_THANH", staff_id=staff_id)
    return get_reservation(conn, code)


def mark_no_shows(conn, now=None):
    """Đánh dấu vắng mặt mọi lượt quá hạn check-in (BR07). Trả về số lượt cập nhật. 1 truy vấn UPDATE + ghi log hàng loạt."""
    now = now or datetime.now()
    limit = now - timedelta(minutes=C.CHECKIN_LATE_MIN)
    ids = [r["ma_dat_ban"] for r in query(conn, "SELECT ma_dat_ban FROM dat_ban WHERE trang_thai='DA_XAC_NHAN' "
                                                "AND thoi_gian_bat_dau < %s", (limit,))]
    if ids:
        marks = ",".join(["%s"] * len(ids))
        execute(conn, f"UPDATE dat_ban SET trang_thai='VANG_MAT' WHERE ma_dat_ban IN ({marks}) AND trang_thai='DA_XAC_NHAN'", ids)
        execute_many(conn, "INSERT INTO nhat_ky_dat_ban (ma_dat_ban, hanh_dong, chi_tiet) VALUES (%s,'VANG_MAT','Tự động')",
                     [(i,) for i in ids])
    return len(ids)


# ============================== UC07 Sơ đồ bàn / UC10 Danh sách khách ==============================
def table_status_map(conn, at=None):
    """Trạng thái từng bàn tại thời điểm `at`: TRONG / DA_DAT / DANG_PHUC_VU / BAO_TRI. Chỉ 2 truy vấn (không N+1)."""
    at = at or datetime.now()
    horizon = at + timedelta(minutes=C.DURATION_MIN)
    tables = query(conn, "SELECT b.*, kv.ten_khu_vuc FROM ban b JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc "
                         "ORDER BY b.ma_khu_vuc, b.ten_ban")
    first = {}
    for d in query(conn, "SELECT d.ma_ban, d.ma_xac_nhan, d.thoi_gian_bat_dau, d.thoi_gian_ket_thuc, d.so_nguoi, "
                         f"d.trang_thai, k.ho_ten FROM dat_ban d JOIN khach_hang k ON k.ma_khach=d.ma_khach "
                         f"WHERE d.trang_thai IN {ACTIVE} AND d.thoi_gian_bat_dau < %s AND d.thoi_gian_ket_thuc > %s "
                         "ORDER BY d.thoi_gian_bat_dau", (horizon, at)):
        first.setdefault(d["ma_ban"], d)
    for t in tables:
        res = first.get(t["ma_ban"])
        t["dat_ban"] = res
        if t["bao_tri"]:
            t["trang_thai"] = "BAO_TRI"
        elif res and res["trang_thai"] == "DA_CHECK_IN":
            t["trang_thai"] = "DANG_PHUC_VU"
        elif res:
            t["trang_thai"] = "DA_DAT"
        else:
            t["trang_thai"] = "TRONG"
    return tables


def guest_list(conn, day, status=None):
    """Danh sách khách theo ngày. Dùng khoảng thời gian (không bọc DATE()) để tận dụng chỉ mục."""
    d0 = datetime.strptime(str(day), "%Y-%m-%d")
    sql = ("SELECT d.ma_xac_nhan, d.thoi_gian_bat_dau, d.so_nguoi, d.trang_thai, d.ghi_chu, b.ten_ban, kv.ten_khu_vuc, "
           "k.ho_ten, k.so_dien_thoai FROM dat_ban d JOIN ban b ON b.ma_ban=d.ma_ban "
           "JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc JOIN khach_hang k ON k.ma_khach=d.ma_khach "
           "WHERE d.thoi_gian_bat_dau >= %s AND d.thoi_gian_bat_dau < %s")
    params = [d0, d0 + timedelta(days=1)]
    if status:
        sql += " AND d.trang_thai=%s"
        params.append(status)
    return query(conn, sql + " ORDER BY d.thoi_gian_bat_dau, b.ten_ban", params)


# ============================== UC06 Đăng nhập ==============================
def authenticate(conn, username, password):
    u = query(conn, "SELECT * FROM nhan_vien WHERE ten_dang_nhap=%s", ((username or "").strip(),), one=True)
    # luôn băm/so khớp để thời gian phản hồi không tiết lộ tài khoản có tồn tại hay không
    ok = check_password_hash(u["mat_khau_hash"] if u else generate_password_hash("x"), password or "")
    if not u or not ok:
        raise BookingError("Sai tên đăng nhập hoặc mật khẩu")
    if not u["kich_hoat"]:
        raise BookingError("Tài khoản đã bị khóa, vui lòng liên hệ quản lý")
    return {"ma_nhan_vien": u["ma_nhan_vien"], "ten_dang_nhap": u["ten_dang_nhap"],
            "ho_ten": u["ho_ten"], "vai_tro": u["vai_tro"]}


# ============================== UC12 Quản lý bàn & khu vực ==============================
def list_tables(conn):
    return query(conn, "SELECT b.*, kv.ten_khu_vuc FROM ban b JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc "
                       "ORDER BY b.ma_khu_vuc, b.ten_ban")


def save_table(conn, ten_ban, ma_khu_vuc, suc_chua, x=0, y=0, ma_ban=None):
    ten_ban = (ten_ban or "").strip()
    if not ten_ban or len(ten_ban) > 20:
        raise BookingError("Tên bàn không được để trống và tối đa 20 ký tự")
    if not 1 <= int(suc_chua) <= C.MAX_PARTY:
        raise BookingError(f"Sức chứa phải từ 1 đến {C.MAX_PARTY}")
    if not query(conn, "SELECT 1 FROM khu_vuc WHERE ma_khu_vuc=%s", (ma_khu_vuc,), one=True):
        raise BookingError("Khu vực không tồn tại")
    try:
        if ma_ban:
            execute(conn, "UPDATE ban SET ten_ban=%s, ma_khu_vuc=%s, suc_chua=%s, vi_tri_x=%s, vi_tri_y=%s WHERE ma_ban=%s",
                    (ten_ban, ma_khu_vuc, suc_chua, x, y, ma_ban))
            return int(ma_ban)
        return execute(conn, "INSERT INTO ban (ten_ban, ma_khu_vuc, suc_chua, vi_tri_x, vi_tri_y) VALUES (%s,%s,%s,%s,%s)",
                       (ten_ban, ma_khu_vuc, suc_chua, x, y))
    except dberr.IntegrityError:
        raise BookingError("Tên bàn đã tồn tại")


def set_maintenance(conn, ma_ban, flag, now=None):
    """Bật bảo trì chỉ khi bàn không còn lượt đặt hiệu lực trong tương lai (BR09)."""
    now = now or datetime.now()
    if flag:
        n = query(conn, f"SELECT COUNT(*) n FROM dat_ban WHERE ma_ban=%s AND trang_thai IN {ACTIVE} "
                        "AND thoi_gian_ket_thuc > %s", (ma_ban, now), one=True)["n"]
        if n:
            raise BookingError(f"Bàn còn {n} lượt đặt chưa phục vụ, hãy xử lý trước khi chuyển sang bảo trì")
    execute(conn, "UPDATE ban SET bao_tri=%s WHERE ma_ban=%s", (1 if flag else 0, ma_ban))


def delete_table(conn, ma_ban):
    if query(conn, "SELECT 1 FROM dat_ban WHERE ma_ban=%s LIMIT 1", (ma_ban,), one=True):
        raise BookingError("Bàn đã có lịch sử đặt, không thể xóa (hãy chuyển sang bảo trì)")
    execute(conn, "DELETE FROM ban WHERE ma_ban=%s", (ma_ban,))


def add_area(conn, ten, mo_ta=None):
    if not (ten or "").strip():
        raise BookingError("Tên khu vực không được để trống")
    try:
        return execute(conn, "INSERT INTO khu_vuc (ten_khu_vuc, mo_ta) VALUES (%s,%s)", (ten.strip(), mo_ta))
    except dberr.IntegrityError:
        raise BookingError("Khu vực đã tồn tại")


def delete_area(conn, ma_khu_vuc):
    if query(conn, "SELECT 1 FROM ban WHERE ma_khu_vuc=%s LIMIT 1", (ma_khu_vuc,), one=True):
        raise BookingError("Khu vực còn bàn, không thể xóa")
    execute(conn, "DELETE FROM khu_vuc WHERE ma_khu_vuc=%s", (ma_khu_vuc,))


# ============================== UC13 Quản lý nhân viên ==============================
def list_staff(conn):
    return query(conn, "SELECT ma_nhan_vien, ten_dang_nhap, ho_ten, vai_tro, kich_hoat FROM nhan_vien ORDER BY ma_nhan_vien")


def _check_password(pw):                                                        # BR11
    if len(pw or "") < C.MIN_PASSWORD_LEN:
        raise BookingError(f"Mật khẩu phải có ít nhất {C.MIN_PASSWORD_LEN} ký tự")


def create_staff(conn, username, ho_ten, password, vai_tro="NHAN_VIEN"):
    username = (username or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_.]{3,30}", username):
        raise BookingError("Tên đăng nhập 3-30 ký tự (chữ, số, _ hoặc .)")
    if not (ho_ten or "").strip():
        raise BookingError("Họ tên không được để trống")
    if vai_tro not in ("NHAN_VIEN", "QUAN_LY"):
        raise BookingError("Vai trò không hợp lệ")
    _check_password(password)
    try:
        return execute(conn, "INSERT INTO nhan_vien (ten_dang_nhap, mat_khau_hash, ho_ten, vai_tro) VALUES (%s,%s,%s,%s)",
                       (username, generate_password_hash(password, method="pbkdf2:sha256"), ho_ten.strip(), vai_tro))
    except dberr.IntegrityError:
        raise BookingError("Tên đăng nhập đã tồn tại")


def set_staff_active(conn, ma_nhan_vien, active):
    if not active:
        row = query(conn, "SELECT vai_tro FROM nhan_vien WHERE ma_nhan_vien=%s", (ma_nhan_vien,), one=True)
        others = query(conn, "SELECT COUNT(*) n FROM nhan_vien WHERE vai_tro='QUAN_LY' AND kich_hoat=1 AND ma_nhan_vien<>%s",
                       (ma_nhan_vien,), one=True)["n"]
        if row and row["vai_tro"] == "QUAN_LY" and others == 0:
            raise BookingError("Không thể khóa quản lý cuối cùng của hệ thống")
    execute(conn, "UPDATE nhan_vien SET kich_hoat=%s WHERE ma_nhan_vien=%s", (1 if active else 0, ma_nhan_vien))


def reset_staff_password(conn, ma_nhan_vien, new_password):
    _check_password(new_password)
    execute(conn, "UPDATE nhan_vien SET mat_khau_hash=%s WHERE ma_nhan_vien=%s",
            (generate_password_hash(new_password, method="pbkdf2:sha256"), ma_nhan_vien))


# ============================== UC14 Nhật ký thao tác ==============================
def audit_log(conn, limit=200):
    return query(conn, "SELECT n.thoi_gian, n.hanh_dong, n.chi_tiet, d.ma_xac_nhan, nv.ho_ten AS nhan_vien "
                       "FROM nhat_ky_dat_ban n JOIN dat_ban d ON d.ma_dat_ban=n.ma_dat_ban "
                       "LEFT JOIN nhan_vien nv ON nv.ma_nhan_vien=n.ma_nhan_vien "
                       "ORDER BY n.ma_nhat_ky DESC LIMIT %s", (int(limit),))
