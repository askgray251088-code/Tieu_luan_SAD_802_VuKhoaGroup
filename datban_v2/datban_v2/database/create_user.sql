-- Tạo user MySQL riêng cho ứng dụng (không dùng root để chạy web).
-- Chạy:  mysql -u root -p < database/create_user.sql
-- *** THAY 'booking123' bằng mật khẩu của bạn, rồi ghi CÙNG mật khẩu đó vào app/config.py (DB_CONFIG["password"]).
-- *** THAY 'localhost' bằng '%' nếu web và MySQL nằm trên 2 máy khác nhau.
CREATE USER IF NOT EXISTS 'booking'@'localhost' IDENTIFIED BY 'booking123';
GRANT ALL PRIVILEGES ON datban.*      TO 'booking'@'localhost';
GRANT ALL PRIVILEGES ON datban_test.* TO 'booking'@'localhost';   -- chỉ cần để chạy pytest
FLUSH PRIVILEGES;



