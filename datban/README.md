# Hệ thống đặt bàn nhà hàng (Python + MySQL)

## Chạy nhanh
```bash
pip install flask mysql-connector-python qrcode pytest
mysql -u root -p < database/schema.sql
mysql -u root -p datban < database/seed.sql
# tạo user: CREATE USER 'booking'@'localhost' IDENTIFIED BY 'booking123'; GRANT ALL ON datban.*, datban_test.* TO 'booking'@'localhost';

python demo.py                           # xem luồng nghiệp vụ chạy trên MySQL
python -m flask --app app.app run        # mở http://localhost:5000
python -m pytest tests -v                # kiểm thử (cần quyền mysql root để tạo datban_test)
```
Trang: `/` đặt bàn · `/tra-cuu` · `/nhan-vien` (sơ đồ bàn + danh sách khách) · `/check-in/<mã>` (đích của QR).
Tài liệu 6 bước nằm trong `docs/`.
