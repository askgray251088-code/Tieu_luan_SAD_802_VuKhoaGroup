from datetime import datetime, timedelta
import pytest
from app import services as S

NOW = datetime(2026, 10, 11, 9, 0)
DAY = datetime(2026, 10, 12)          # ngày đặt thử
T19 = DAY.replace(hour=19)


def book(conn, start=T19, party=2, sdt="0987654321", **kw):
    return S.create_reservation(conn, "Lê Test", sdt, start, party, now=NOW, **kw)


def test_dat_ban_thanh_cong_chon_ban_vua_nhat(conn):
    r = book(conn, party=2)
    assert r["trang_thai"] == "DA_XAC_NHAN" and len(r["ma_xac_nhan"]) == 8
    assert r["suc_chua"] == 2                       # bàn 2 chỗ, không chiếm bàn lớn
    assert r["thoi_gian_ket_thuc"] == T19 + timedelta(minutes=90)


def test_khong_dat_trung_ban_cung_khung_gio(conn):
    r1 = book(conn, party=2, ma_ban=1, sdt="0900000001")
    with pytest.raises(S.BookingError):
        book(conn, party=2, ma_ban=1, sdt="0900000002")
    # không chỉ định bàn -> hệ thống tự xếp bàn khác
    r2 = book(conn, party=2, sdt="0900000002")
    assert r2["ma_ban"] != r1["ma_ban"]


def test_dem_don_ban_15_phut(conn):
    t12 = DAY.replace(hour=12)
    book(conn, start=t12, ma_ban=1, sdt="0900000001")       # kết thúc 13:30
    with pytest.raises(S.BookingError):
        book(conn, start=t12.replace(hour=13, minute=35), ma_ban=1, sdt="0900000002")   # trong 15' dọn bàn
    ok = book(conn, start=t12.replace(hour=13, minute=45), ma_ban=1, sdt="0900000002")  # đúng 15' sau
    assert ok["ma_ban"] == 1


def test_het_ban_cho_nhom_dong(conn):
    book(conn, party=12, sdt="0900000001")                  # V2 (12 chỗ)
    with pytest.raises(S.BookingError):
        book(conn, party=12, sdt="0900000002")


@pytest.mark.parametrize("start,party,sdt", [
    (DAY.replace(hour=9), 2, "0900000001"),                 # trước giờ mở cửa
    (DAY.replace(hour=21), 2, "0900000001"),                # kết thúc sau 22:00
    (NOW + timedelta(minutes=30), 2, "0900000001"),         # đặt gấp < 60'
    (NOW + timedelta(days=40), 2, "0900000001"),            # quá 30 ngày
    (T19, 0, "0900000001"),                                 # số người sai
    (T19, 25, "0900000001"),
    (T19, 2, "12345"),                                      # sđt sai
])
def test_validate_dau_vao(conn, start, party, sdt):
    with pytest.raises(S.BookingError):
        book(conn, start=start, party=party, sdt=sdt)


def test_doi_gio_va_tu_doi_ban_khi_can(conn):
    r = book(conn, party=2, ma_ban=1)
    r2 = S.modify_reservation(conn, r["ma_xac_nhan"], new_party=5, now=NOW)   # cần bàn >=5 chỗ
    assert r2["suc_chua"] >= 5 and r2["so_nguoi"] == 5
    r3 = S.modify_reservation(conn, r["ma_xac_nhan"], new_start=T19.replace(hour=12), now=NOW)
    assert r3["thoi_gian_bat_dau"].hour == 12


def test_huy_va_gioi_han_thoi_gian(conn):
    r = book(conn)
    with pytest.raises(S.BookingError):                      # còn < 2 giờ -> không được hủy
        S.cancel_reservation(conn, r["ma_xac_nhan"], now=T19 - timedelta(hours=1))
    h = S.cancel_reservation(conn, r["ma_xac_nhan"], now=NOW)
    assert h["trang_thai"] == "DA_HUY"
    # bàn được giải phóng
    assert S.find_available_tables(conn, T19, 2)[0]["ma_ban"] == r["ma_ban"]


def test_checkin_cua_so_thoi_gian(conn):
    r = book(conn)
    code = r["ma_xac_nhan"]
    with pytest.raises(S.BookingError):
        S.check_in(conn, code, now=T19 - timedelta(minutes=30))   # quá sớm
    with pytest.raises(S.BookingError):
        S.check_in(conn, code, now=T19 + timedelta(minutes=20))   # quá muộn
    ok = S.check_in(conn, code, now=T19 - timedelta(minutes=5))
    assert ok["trang_thai"] == "DA_CHECK_IN"
    assert S.complete(conn, code)["trang_thai"] == "HOAN_THANH"


def test_vang_mat_va_so_do_ban(conn):
    r = book(conn)
    at = T19 + timedelta(minutes=5)
    status = {t["ten_ban"]: t["trang_thai"] for t in S.table_status_map(conn, at)}
    assert status[r["ten_ban"]] == "DA_DAT"
    assert S.mark_no_shows(conn, now=T19 + timedelta(minutes=16)) == 1
    assert S.get_reservation(conn, r["ma_xac_nhan"])["trang_thai"] == "VANG_MAT"


def test_khach_cu_khong_bi_nhan_doi(conn):
    book(conn, sdt="0911111111")
    book(conn, start=T19.replace(hour=12), sdt="0911111111")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM khach_hang WHERE so_dien_thoai='0911111111'")
    assert cur.fetchone()[0] == 1
