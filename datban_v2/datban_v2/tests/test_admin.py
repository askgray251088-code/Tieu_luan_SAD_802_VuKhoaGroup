from datetime import datetime
import pytest
from app import services as S

NOW = datetime(2026, 10, 11, 9, 0)


def test_dang_nhap(conn):
    assert S.authenticate(conn, "admin", "Admin@123")["vai_tro"] == "QUAN_LY"
    for u, p in [("admin", "sai"), ("khong_co", "x"), ("", "")]:
        with pytest.raises(S.BookingError):
            S.authenticate(conn, u, p)


def test_quan_ly_nhan_vien(conn):
    ma = S.create_staff(conn, "an.nv", "Nguyễn An", "matkhau1")
    assert S.authenticate(conn, "an.nv", "matkhau1")["ho_ten"] == "Nguyễn An"
    with pytest.raises(S.BookingError):
        S.create_staff(conn, "an.nv", "Trùng", "matkhau1")          # trùng tên đăng nhập
    with pytest.raises(S.BookingError):
        S.create_staff(conn, "ab", "Ngắn", "123")                   # tên và mật khẩu không hợp lệ
    S.set_staff_active(conn, ma, False)
    with pytest.raises(S.BookingError):
        S.authenticate(conn, "an.nv", "matkhau1")                   # bị khóa
    S.reset_staff_password(conn, ma, "matkhau2")
    S.set_staff_active(conn, ma, True)
    assert S.authenticate(conn, "an.nv", "matkhau2")
    with pytest.raises(S.BookingError):
        S.set_staff_active(conn, 1, False)                          # không khóa quản lý cuối cùng


def test_quan_ly_ban_va_bao_tri(conn):
    ma = S.save_table(conn, "C1", 1, 6, 10, 10)
    with pytest.raises(S.BookingError):
        S.save_table(conn, "C1", 1, 6)                              # trùng tên
    with pytest.raises(S.BookingError):
        S.save_table(conn, "C2", 1, 50)                             # sức chứa quá lớn
    S.save_table(conn, "C1-moi", 1, 8, 10, 10, ma_ban=ma)
    r = S.create_reservation(conn, "Khách", "0900000009", datetime(2026, 10, 12, 19), 8, ma_ban=ma, now=NOW)
    with pytest.raises(S.BookingError):
        S.set_maintenance(conn, ma, True, now=NOW)                  # còn lượt đặt
    with pytest.raises(S.BookingError):
        S.delete_table(conn, ma)                                    # có lịch sử
    S.cancel_reservation(conn, r["ma_xac_nhan"], now=NOW)
    S.set_maintenance(conn, ma, True, now=NOW)
    assert ma not in [t["ma_ban"] for t in S.find_available_tables(conn, datetime(2026, 10, 12, 19), 8)]


def test_xoa_ban_chua_dung_va_khu_vuc(conn):
    ma = S.save_table(conn, "TMP", 1, 2)
    S.delete_table(conn, ma)
    kv = S.add_area(conn, "Ban công")
    S.delete_area(conn, kv)
    with pytest.raises(S.BookingError):
        S.delete_area(conn, 1)                                      # khu vực còn bàn
