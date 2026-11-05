"""CẤU HÌNH TOÀN HỆ THỐNG
=====================================================================
Ký hiệu  ***  đánh dấu những chỗ BẠN CẦN THAY ĐỔI khi chạy trên máy khác.
Cách nhanh nhất: KHÔNG sửa file này mà đặt biến môi trường (xem cột "Biến môi trường").
  Windows (CMD):   set DATBAN_PASSWORD=matkhau_cua_ban
  Windows (PowerShell):  $env:DATBAN_PASSWORD="matkhau_cua_ban"
  Linux / macOS:   export DATBAN_PASSWORD=matkhau_cua_ban
=====================================================================
"""
import os

# ================== *** PHẦN 1 - KẾT NỐI MYSQL (BẮT BUỘC KIỂM TRA) *** ==================
DB_CONFIG = {
    # *** THAY: địa chỉ máy chạy MySQL. Cùng máy = "127.0.0.1" hoặc "localhost";
    # ***       máy khác / cloud = IP hoặc tên miền của máy chủ MySQL.   [Biến: DATBAN_HOST]
    "host": os.getenv("DATBAN_HOST", "127.0.0.1"),
    # *** THAY: cổng MySQL. Mặc định 3306 (XAMPP, MySQL Installer); MAMP thường là 8889.  [DATBAN_PORT]
    "port": int(os.getenv("DATBAN_PORT", "3306")),
    # *** THAY: tên user MySQL. Mặc định "booking" (tạo bằng database/create_user.sql). [DATBAN_USER]
    "user": os.getenv("DATBAN_USER", "booking"),
    # *** THAY: mật khẩu của user trên. PHẢI trùng với mật khẩu đã đặt trong create_user.sql. [DATBAN_PASSWORD]
    "password": os.getenv("DATBAN_PASSWORD", "booking123"),
    # Tên CSDL. Giữ "datban" nếu bạn dùng nguyên schema.sql.   [DATBAN_DB]
    "database": os.getenv("DATBAN_DB", "datban"),
}
POOL_SIZE = int(os.getenv("DATBAN_POOL", "5"))   # số kết nối MySQL giữ sẵn (tăng lên 10-20 nếu nhiều người truy cập)

# ================== *** PHẦN 2 - WEB SERVER *** ==================
# *** THAY khi triển khai thật: chuỗi bí mật dài, ngẫu nhiên (dùng để ký phiên đăng nhập). [DATBAN_SECRET]
SECRET_KEY = os.getenv("DATBAN_SECRET", "dev-only-change-me")
# *** THAY: "127.0.0.1" = chỉ máy này truy cập. Đổi thành "0.0.0.0" để điện thoại/máy khác
# ***       trong cùng mạng Wi-Fi truy cập được (cần để nhân viên quét QR bằng điện thoại).  [DATBAN_WEB_HOST]
WEB_HOST = os.getenv("DATBAN_WEB_HOST", "127.0.0.1")
# *** THAY nếu cổng 5000 đang bị chương trình khác dùng. [DATBAN_WEB_PORT]
WEB_PORT = int(os.getenv("DATBAN_WEB_PORT", "5000"))
# *** THAY: địa chỉ mà ĐIỆN THOẠI dùng để mở web, ví dụ "http://192.168.1.10:5000" (IP máy chạy server).
# ***       Địa chỉ này được mã hóa vào mã QR. Để trống = dùng địa chỉ trình duyệt đang mở
# ***       (sẽ KHÔNG quét được bằng điện thoại nếu đang mở bằng localhost).  [DATBAN_BASE_URL]
BASE_URL = os.getenv("DATBAN_BASE_URL", "").rstrip("/")
# *** THAY: đặt False khi triển khai thật (debug=True làm lộ mã nguồn khi lỗi). [DATBAN_DEBUG=0/1]
DEBUG = os.getenv("DATBAN_DEBUG", "1") == "1"
# Giới hạn chống spam: tối đa N lần gửi form đặt bàn / đăng nhập trong 60 giây cho mỗi địa chỉ IP
RATE_LIMIT_PER_MIN = int(os.getenv("DATBAN_RATE", "10"))
# Tự quét "vắng mặt" mỗi N giây trong lúc server chạy (0 = tắt)
NO_SHOW_SCAN_SECONDS = int(os.getenv("DATBAN_SCAN", "60"))

# ================== BUSINESS RULES (xem docs: Đặc tả, mục Business Rules) ==================
# *** THAY nếu nhà hàng của bạn có quy định khác; không cần sửa chỗ nào khác trong code.
OPEN_HOUR = 10            # BR01 giờ mở cửa
CLOSE_HOUR = 22           # BR01 giờ đóng cửa
DURATION_MIN = 90         # BR02 thời lượng một lượt đặt (phút)
BUFFER_MIN = 15           # BR03 thời gian dọn bàn giữa 2 lượt (phút)
MIN_ADVANCE_MIN = 60      # BR04 đặt trước tối thiểu (phút)
MAX_ADVANCE_DAYS = 30     # BR04 đặt trước tối đa (ngày)
MAX_PARTY = 20            # BR05 số người tối đa / lượt
CANCEL_BEFORE_MIN = 120   # BR06 chỉ đổi/hủy khi còn tối thiểu ... phút trước giờ đặt
CHECKIN_EARLY_MIN = 15    # BR07 check-in sớm nhất (phút trước giờ đặt)
CHECKIN_LATE_MIN = 15     # BR07 check-in muộn nhất (phút sau giờ đặt) - quá hạn => vắng mặt
MIN_PASSWORD_LEN = 6      # BR11 độ dài mật khẩu tối thiểu của nhân viên
