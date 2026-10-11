# Bước 5 – Triển khai & Bước 6 – Bảo trì

## Triển khai
1. Cài MySQL 8, tạo người dùng riêng: `CREATE USER 'booking'@'localhost' IDENTIFIED BY '<mật khẩu mạnh>'; GRANT ALL ON datban.* TO 'booking'@'localhost';`
2. Nạp CSDL: `mysql -u root -p < database/schema.sql` rồi `mysql -u root -p datban < database/seed.sql`.
3. Cấu hình bằng biến môi trường: `DATBAN_HOST`, `DATBAN_PORT`, `DATBAN_USER`, `DATBAN_PASSWORD`, `DATBAN_DB`. Đổi `secret_key` trong `app/app.py`.
4. Chạy thử: `python -m flask --app app.app run`; chạy thật: `gunicorn app.app:app -b 0.0.0.0:8000`.
5. Nghiệm thu: chạy `pytest`, đặt 1 bàn thật, quét QR check-in.

## Bảo trì
- **Sao lưu:** `mysqldump -u root -p datban > backup_$(date +%F).sql` hằng ngày.
- **Định kỳ:** dọn `nhat_ky_dat_ban` cũ; cho `mark_no_shows` chạy theo lịch (cron mỗi 5 phút) thay vì chỉ khi nhân viên mở trang.
- **Thay đổi rule:** chỉ sửa `config.py`, chạy lại test.
- **Hạn chế hiện tại / mở rộng:** chưa có đăng nhập nhân viên (trang `/nhan-vien` đang mở), chưa gửi SMS/email xác nhận, chưa ghép nhiều bàn cho nhóm rất đông, chưa đặt cọc.
