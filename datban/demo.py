"""Chạy thử toàn bộ luồng nghiệp vụ trên MySQL (không cần mở web).
Cách chạy:  python demo.py
"""
from datetime import datetime, timedelta
from app import services as S
from app.db import get_conn, execute

conn = get_conn()
execute(conn, "DELETE FROM nhat_ky_dat_ban")
execute(conn, "DELETE FROM dat_ban")

NOW = datetime.now().replace(second=0, microsecond=0)
DAY = (NOW + timedelta(days=1)).replace(hour=19, minute=0)   # tối mai 19:00


def buoc(t):
    print(f"\n=== {t} ===")


def thu(label, fn):
    try:
        r = fn()
        print(f"[OK ] {label}")
        return r
    except S.BookingError as e:
        print(f"[LOI] {label} -> {e}")


buoc("1. Tra cứu bàn trống cho 4 người lúc " + DAY.strftime("%d/%m %H:%M"))
for t in S.find_available_tables(conn, DAY, 4):
    print(f"   {t['ten_ban']:3} {t['suc_chua']:2} chỗ  {t['ten_khu_vuc']}")

buoc("2. Đặt bàn")
r1 = thu("An đặt 4 người", lambda: S.create_reservation(conn, "Nguyễn Văn An", "0901234567", DAY, 4))
print(f"   -> mã {r1['ma_xac_nhan']}, bàn {r1['ten_ban']}, {r1['thoi_gian_bat_dau']:%H:%M}-{r1['thoi_gian_ket_thuc']:%H:%M}")
r2 = thu("Bình đặt 4 người (cùng giờ)", lambda: S.create_reservation(conn, "Trần Thị Bình", "0912345678", DAY, 4))
print(f"   -> hệ thống tự xếp bàn {r2['ten_ban']} (bàn {r1['ten_ban']} đã có người)")

buoc("3. Vi phạm business rule")
thu("Đặt 30 người", lambda: S.create_reservation(conn, "Cường", "0922222222", DAY, 30))
thu("Đặt lúc 09:00 (trước giờ mở cửa)", lambda: S.create_reservation(conn, "Cường", "0922222222", DAY.replace(hour=9), 2))
thu("Đặt gấp sau 20 phút", lambda: S.create_reservation(conn, "Cường", "0922222222", NOW + timedelta(minutes=20), 2))
thu("SĐT sai định dạng", lambda: S.create_reservation(conn, "Cường", "abc", DAY, 2))

buoc("4. Đổi lịch và hủy")
r1 = thu("An đổi sang 6 người", lambda: S.modify_reservation(conn, r1["ma_xac_nhan"], new_party=6))
print(f"   -> hệ thống chuyển sang bàn {r1['ten_ban']} ({r1['suc_chua']} chỗ)")
thu("Bình hủy đặt bàn", lambda: S.cancel_reservation(conn, r2["ma_xac_nhan"]))

buoc("5. Ngày đến: check-in, phục vụ, trả bàn (mô phỏng thời gian)")
code = r1["ma_xac_nhan"]
thu("Check-in sớm 1 giờ", lambda: S.check_in(conn, code, now=DAY - timedelta(hours=1)))
thu("Check-in lúc 18:50", lambda: S.check_in(conn, code, now=DAY - timedelta(minutes=10)))
st = {t["ten_ban"]: t["trang_thai"] for t in S.table_status_map(conn, DAY + timedelta(minutes=30))}
print("   Sơ đồ bàn 19:30 :", ", ".join(f"{k}={v}" for k, v in st.items() if v != "TRONG"))
thu("Hoàn thành lượt đặt", lambda: S.complete(conn, code))

buoc("6. Nhật ký thao tác (bảng nhat_ky_dat_ban)")
for row in S.query(conn, "SELECT ma_dat_ban, hanh_dong, chi_tiet FROM nhat_ky_dat_ban ORDER BY ma_nhat_ky"):
    print(f"   #{row['ma_dat_ban']} {row['hanh_dong']:10} {row['chi_tiet'] or ''}")
