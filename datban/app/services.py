"""Tầng nghiệp vụ: toàn bộ business rules nằm ở đây (không phụ thuộc Flask)."""
import re
import secrets
import string
from datetime import datetime, timedelta

from . import config as C
from .db import execute, query, transaction

ACTIVE = "('DA_XAC_NHAN','DA_CHECK_IN')"


class BookingError(Exception):
    """Lỗi vi phạm business rule, có thể hiển thị cho người dùng."""


# ---------- tiện ích ----------
def _gen_code(conn):
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = "".join(secrets.choice(alphabet) for _ in range(8))
        if not query(conn, "SELECT 1 FROM dat_ban WHERE ma_xac_nhan=%s", (code,), one=True):
            return code
    raise BookingError("Không tạo được mã xác nhận, vui lòng thử lại")


def _log(conn, ma_dat_ban, action, detail=""):
    execute(conn, "INSERT INTO nhat_ky_dat_ban (ma_dat_ban, hanh_dong, chi_tiet) VALUES (%s,%s,%s)",
            (ma_dat_ban, action, detail))


def _validate_time(start, party, now, check_advance=True):
    end = start + timedelta(minutes=C.DURATION_MIN)
    if not 1 <= party <= C.MAX_PARTY:
        raise BookingError(f"Số người phải từ 1 đến {C.MAX_PARTY}")
    open_t = start.replace(hour=C.OPEN_HOUR, minute=0, second=0, microsecond=0)
    close_t = start.replace(hour=C.CLOSE_HOUR, minute=0, second=0, microsecond=0)
    if start < open_t or end > close_t:
        raise BookingError(f"Nhà hàng mở {C.OPEN_HOUR}:00-{C.CLOSE_HOUR}:00; "
                           f"lượt đặt kéo dài {C.DURATION_MIN} phút nên giờ đến muộn nhất là "
                           f"{(close_t - timedelta(minutes=C.DURATION_MIN)).strftime('%H:%M')}")
    if check_advance:
        if start < now + timedelta(minutes=C.MIN_ADVANCE_MIN):
            raise BookingError(f"Phải đặt trước ít nhất {C.MIN_ADVANCE_MIN} phút")
        if start > now + timedelta(days=C.MAX_ADVANCE_DAYS):
            raise BookingError(f"Chỉ nhận đặt trước tối đa {C.MAX_ADVANCE_DAYS} ngày")
    return end


def _validate_customer(ho_ten, sdt):
    if not ho_ten or not ho_ten.strip():
        raise BookingError("Họ tên không được để trống")
    if not re.fullmatch(r"0\d{9,10}", sdt or ""):
        raise BookingError("Số điện thoại không hợp lệ (10-11 số, bắt đầu bằng 0)")


def _conflict(conn, ma_ban, start, end, exclude_id=None):
    sql = (f"SELECT ma_dat_ban FROM dat_ban WHERE ma_ban=%s AND trang_thai IN {ACTIVE} "
           "AND thoi_gian_bat_dau < %s AND thoi_gian_ket_thuc > %s")
    params = [ma_ban, end + timedelta(minutes=C.BUFFER_MIN), start - timedelta(minutes=C.BUFFER_MIN)]
    if exclude_id:
        sql += " AND ma_dat_ban <> %s"
        params.append(exclude_id)
    return query(conn, sql, params, one=True) is not None


# ---------- tra cứu / kiểm tra khả dụng ----------
def find_available_tables(conn, start, party, area_id=None, exclude_id=None):
    """Bàn trống phù hợp, sắp theo sức chứa tăng dần (bàn vừa nhất đứng đầu)."""
    end = start + timedelta(minutes=C.DURATION_MIN)
    sql = ("SELECT b.ma_ban, b.ten_ban, b.suc_chua, kv.ten_khu_vuc, b.ma_khu_vuc "
           "FROM ban b JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc "
           "WHERE b.bao_tri=0 AND b.suc_chua>=%s")
    params = [party]
    if area_id:
        sql += " AND b.ma_khu_vuc=%s"
        params.append(int(area_id))
    sql += (f" AND NOT EXISTS (SELECT 1 FROM dat_ban d WHERE d.ma_ban=b.ma_ban "
            f"AND d.trang_thai IN {ACTIVE} AND d.thoi_gian_bat_dau < %s AND d.thoi_gian_ket_thuc > %s")
    params += [end + timedelta(minutes=C.BUFFER_MIN), start - timedelta(minutes=C.BUFFER_MIN)]
    if exclude_id:
        sql += " AND d.ma_dat_ban <> %s"
        params.append(exclude_id)
    sql += ") ORDER BY b.suc_chua, b.ten_ban"
    return query(conn, sql, params)


def list_areas(conn):
    return query(conn, "SELECT * FROM khu_vuc ORDER BY ma_khu_vuc")


# ---------- đặt / đổi / hủy ----------
def create_reservation(conn, ho_ten, sdt, start, party, email=None, ma_ban=None,
                       area_id=None, ghi_chu=None, now=None):
    now = now or datetime.now()
    _validate_customer(ho_ten, sdt)
    end = _validate_time(start, party, now)

    with transaction(conn):
        if ma_ban:
            candidates = [int(ma_ban)]
        else:
            candidates = [t["ma_ban"] for t in find_available_tables(conn, start, party, area_id)]
        chosen = None
        for tid in candidates:
            # khóa dòng bàn để 2 người không đặt trùng cùng lúc
            ban = query(conn, "SELECT * FROM ban WHERE ma_ban=%s FOR UPDATE", (tid,), one=True)
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
        rid = execute(conn,
                      "INSERT INTO dat_ban (ma_xac_nhan, ma_khach, ma_ban, thoi_gian_bat_dau, thoi_gian_ket_thuc, "
                      "so_nguoi, ghi_chu) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                      (code, ma_khach, chosen["ma_ban"], start, end, party, ghi_chu))
        _log(conn, rid, "TAO", f"Bàn {chosen['ten_ban']}, {party} người")
    return get_reservation(conn, code)


def get_reservation(conn, code):
    r = query(conn,
              "SELECT d.*, b.ten_ban, b.suc_chua, kv.ten_khu_vuc, k.ho_ten, k.so_dien_thoai, k.email "
              "FROM dat_ban d JOIN ban b ON b.ma_ban=d.ma_ban "
              "JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc "
              "JOIN khach_hang k ON k.ma_khach=d.ma_khach WHERE d.ma_xac_nhan=%s", (code.upper().strip(),), one=True)
    if not r:
        raise BookingError("Không tìm thấy mã đặt bàn")
    return r


def _require_changeable(r, now):
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


# ---------- nhân viên: check-in, hoàn thành, vắng mặt ----------
def check_in(conn, code, now=None):
    now = now or datetime.now()
    r = get_reservation(conn, code)
    if r["trang_thai"] != "DA_XAC_NHAN":
        raise BookingError(f"Không thể check-in: lượt đặt đang ở trạng thái {r['trang_thai']}")
    earliest = r["thoi_gian_bat_dau"] - timedelta(minutes=C.CHECKIN_EARLY_MIN)
    latest = r["thoi_gian_bat_dau"] + timedelta(minutes=C.CHECKIN_LATE_MIN)
    if now < earliest:
        raise BookingError(f"Chưa đến giờ check-in (từ {earliest:%H:%M})")
    if now > latest:
        raise BookingError(f"Đã quá hạn check-in ({latest:%H:%M}); lượt đặt có thể bị đánh dấu vắng mặt")
    execute(conn, "UPDATE dat_ban SET trang_thai='DA_CHECK_IN', gio_check_in=%s WHERE ma_dat_ban=%s",
            (now, r["ma_dat_ban"]))
    _log(conn, r["ma_dat_ban"], "CHECK_IN")
    return get_reservation(conn, code)


def complete(conn, code, now=None):
    r = get_reservation(conn, code)
    if r["trang_thai"] != "DA_CHECK_IN":
        raise BookingError("Chỉ hoàn thành được lượt đặt đã check-in")
    execute(conn, "UPDATE dat_ban SET trang_thai='HOAN_THANH' WHERE ma_dat_ban=%s", (r["ma_dat_ban"],))
    _log(conn, r["ma_dat_ban"], "HOAN_THANH")
    return get_reservation(conn, code)


def mark_no_shows(conn, now=None):
    """Đánh dấu vắng mặt các lượt đã quá hạn check-in (BR07). Trả về số lượt cập nhật."""
    now = now or datetime.now()
    limit = now - timedelta(minutes=C.CHECKIN_LATE_MIN)
    rows = query(conn, "SELECT ma_dat_ban FROM dat_ban WHERE trang_thai='DA_XAC_NHAN' "
                       "AND thoi_gian_bat_dau < %s", (limit,))
    for row in rows:
        execute(conn, "UPDATE dat_ban SET trang_thai='VANG_MAT' WHERE ma_dat_ban=%s", (row["ma_dat_ban"],))
        _log(conn, row["ma_dat_ban"], "VANG_MAT")
    return len(rows)


# ---------- báo cáo cho nhân viên ----------
def table_status_map(conn, at=None):
    """Trạng thái từng bàn tại thời điểm `at`: TRONG / DA_DAT / DANG_PHUC_VU / BAO_TRI."""
    at = at or datetime.now()
    tables = query(conn, "SELECT b.*, kv.ten_khu_vuc FROM ban b JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc "
                         "ORDER BY b.ma_khu_vuc, b.ten_ban")
    horizon = at + timedelta(minutes=C.DURATION_MIN)
    for t in tables:
        res = query(conn,
                    "SELECT d.ma_xac_nhan, d.thoi_gian_bat_dau, d.thoi_gian_ket_thuc, d.so_nguoi, d.trang_thai, k.ho_ten "
                    f"FROM dat_ban d JOIN khach_hang k ON k.ma_khach=d.ma_khach WHERE d.ma_ban=%s "
                    f"AND d.trang_thai IN {ACTIVE} AND d.thoi_gian_bat_dau < %s AND d.thoi_gian_ket_thuc > %s "
                    "ORDER BY d.thoi_gian_bat_dau LIMIT 1", (t["ma_ban"], horizon, at), one=True)
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
    sql = ("SELECT d.ma_xac_nhan, d.thoi_gian_bat_dau, d.so_nguoi, d.trang_thai, d.ghi_chu, "
           "b.ten_ban, kv.ten_khu_vuc, k.ho_ten, k.so_dien_thoai "
           "FROM dat_ban d JOIN ban b ON b.ma_ban=d.ma_ban JOIN khu_vuc kv ON kv.ma_khu_vuc=b.ma_khu_vuc "
           "JOIN khach_hang k ON k.ma_khach=d.ma_khach WHERE DATE(d.thoi_gian_bat_dau)=%s")
    params = [day]
    if status:
        sql += " AND d.trang_thai=%s"
        params.append(status)
    sql += " ORDER BY d.thoi_gian_bat_dau, b.ten_ban"
    return query(conn, sql, params)


def find_by_phone(conn, sdt):
    return query(conn,
                 "SELECT d.ma_xac_nhan, d.thoi_gian_bat_dau, d.so_nguoi, d.trang_thai, b.ten_ban "
                 "FROM dat_ban d JOIN ban b ON b.ma_ban=d.ma_ban JOIN khach_hang k ON k.ma_khach=d.ma_khach "
                 "WHERE k.so_dien_thoai=%s ORDER BY d.thoi_gian_bat_dau DESC", (sdt,))
