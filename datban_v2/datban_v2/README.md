# Hệ thống đặt bàn Nhà hàng Hương Việt (Python + Flask + MySQL 8)

> Ký hiệu **`***`** trong code = chỗ bạn **cần kiểm tra / thay đổi** khi chạy trên máy khác.
> Tìm nhanh toàn bộ: `grep -rn "\*\*\*" app database tests run.py demo.py` (Windows: Ctrl+Shift+F, gõ `***`).

## 1. Những chỗ CẦN THAY để chạy được

| # | File | Giá trị mặc định | Thay bằng gì | Bắt buộc? |
|---|------|------------------|--------------|-----------|
| 1 | `app/config.py` → `DB_CONFIG["host"]` | `127.0.0.1` | `localhost` / IP máy chạy MySQL (MySQL ở máy khác hoặc cloud) | Chỉ khi MySQL không cùng máy |
| 2 | `app/config.py` → `DB_CONFIG["port"]` | `3306` | Cổng MySQL của bạn (MAMP thường `8889`) | Chỉ khi cổng khác |
| 3 | `app/config.py` → `DB_CONFIG["user"]` | `booking` | User MySQL bạn đã tạo | Có, nếu bạn đổi tên user |
| 4 | `app/config.py` → `DB_CONFIG["password"]` và `database/create_user.sql` | `booking123` | Mật khẩu của bạn (**hai nơi phải giống nhau**) | **Có** |
| 5 | `app/config.py` → `WEB_HOST` | `127.0.0.1` | `0.0.0.0` để điện thoại cùng Wi-Fi truy cập | Khi cần quét QR bằng điện thoại |
| 6 | `app/config.py` → `BASE_URL` | *(trống)* | `http://<IP máy tính>:5000` (xem IP: `ipconfig` / `ifconfig`) — được mã hóa vào QR | Khi cần quét QR bằng điện thoại |
| 7 | `app/config.py` → `SECRET_KEY` | `dev-only-change-me` | Chuỗi ngẫu nhiên dài | Khi triển khai thật |
| 8 | `app/config.py` → `DEBUG` | `True` | `False` khi triển khai thật | Khi triển khai thật |
| 9 | `database/seed.sql` (tài khoản mẫu) | `admin/Admin@123`, `nhanvien/Nhanvien@123` | Đổi mật khẩu trong menu **Nhân sự** sau khi đăng nhập | Khi triển khai thật |
| 10 | `tests/conftest.py` → `ROOT_USER`, `ROOT_PASSWORD` | `root`, *(trống)* | Tài khoản MySQL có quyền tạo CSDL (biến `DATBAN_ROOT_USER`, `DATBAN_ROOT_PASSWORD`) | Chỉ khi chạy `pytest` |

**Cách không cần sửa file:** đặt biến môi trường (tên trong ngoặc ở `config.py`), ví dụ
- Windows CMD: `set DATBAN_PASSWORD=matkhau_cua_ban`
- PowerShell: `$env:DATBAN_PASSWORD="matkhau_cua_ban"`
- Linux/macOS: `export DATBAN_PASSWORD=matkhau_cua_ban`

## 2. Cài đặt và chạy (5 bước)

```bash
# Bước 1. Thư viện Python (Python 3.10+)
pip install flask mysql-connector-python qrcode pytest

# Bước 2. Tạo CSDL + bảng  (*** nhập mật khẩu root MySQL khi được hỏi; lệnh sẽ XÓA CSDL "datban" cũ)
mysql -u root -p < database/schema.sql

# Bước 3. Nạp dữ liệu mẫu (11 bàn, 3 khu vực, 2 tài khoản)
mysql -u root -p datban < database/seed.sql

# Bước 4. Tạo user cho ứng dụng  (*** sửa mật khẩu trong file trước khi chạy, rồi ghi cùng mật khẩu vào config.py)
mysql -u root -p < database/create_user.sql

# Bước 5. Chạy
python demo.py        # xem toàn bộ luồng nghiệp vụ chạy trên MySQL (không cần web)
python run.py         # mở web: http://localhost:5000
python -m pytest tests -v   # 28 bài kiểm thử
```

Trang chính: `/` đặt bàn · `/tra-cuu` · `/dang-nhap` · `/nhan-vien` (sơ đồ bàn + danh sách khách + check-in) · `/quan-ly/ban` · `/quan-ly/nhan-su` · `/quan-ly/nhat-ky`.

## 3. Cho nhân viên quét QR bằng điện thoại
1. Máy tính và điện thoại **cùng mạng Wi-Fi**.
2. Lấy IP máy tính (vd `192.168.1.10`). Đặt `WEB_HOST = "0.0.0.0"` và `BASE_URL = "http://192.168.1.10:5000"` trong `config.py`.
3. Cho phép cổng 5000 qua tường lửa nếu hệ điều hành hỏi. Chạy lại `python run.py`.
4. Đặt bàn trên máy tính → mã QR hiện ra → dùng điện thoại quét → đăng nhập nhân viên → bấm **Check-in**.

## 4. Lỗi thường gặp
| Thông báo | Nguyên nhân / cách xử lý |
|-----------|--------------------------|
| `Access denied for user 'booking'` | Mật khẩu trong `config.py` khác mật khẩu trong `create_user.sql`. Sửa cho trùng, hoặc chạy lại bước 4 |
| `Can't connect to MySQL server on '127.0.0.1:3306'` | MySQL chưa chạy, hoặc sai `host`/`port` (mục 1, dòng 1-2) |
| `Unknown database 'datban'` | Chưa chạy bước 2 |
| Tiếng Việt thành `NhÃ ` | Nạp SQL bằng công cụ không dùng UTF-8: chạy bằng `mysql ... --default-character-set=utf8mb4` |
| `Address already in use` | Cổng 5000 bị chiếm: đổi `WEB_PORT` |
| Điện thoại quét QR nhưng không mở được | Chưa đặt `BASE_URL` đúng IP, hoặc điện thoại khác mạng Wi-Fi |
| `Phiên làm việc không hợp lệ (CSRF)` | Trang mở quá lâu / cookie bị chặn: tải lại trang |
| `pytest` báo `Access denied for user 'root'` | Đặt `DATBAN_ROOT_USER` / `DATBAN_ROOT_PASSWORD` (mục 1, dòng 10) |

## 5. Cấu trúc
```
database/  schema.sql  seed.sql  create_user.sql      # MySQL
app/       config.py  db.py  services.py  app.py      # cấu hình · kết nối · nghiệp vụ (UC01-UC14) · giao diện web
           templates/  static/
tests/     test_booking.py  test_admin.py  test_web.py
run.py  demo.py                                        # khởi chạy web · chạy thử nghiệp vụ
docs/      Dac_ta_He_thong_Dat_ban_Huong_Viet.docx    # tài liệu đặc tả (khuôn mẫu FaceShop)
```
