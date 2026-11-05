SET NAMES utf8mb4;
-- Dữ liệu mẫu. Chạy:  mysql -u root -p datban < database/seed.sql
-- *** BẢO MẬT: 2 tài khoản bên dưới chỉ để thử nghiệm.
-- ***   admin / Admin@123     (Quản lý)      nhanvien / Nhanvien@123  (Nhân viên)
-- *** Khi triển khai thật: đăng nhập admin -> menu "Nhân sự" -> đặt lại mật khẩu.
INSERT INTO khu_vuc (ten_khu_vuc, mo_ta) VALUES
 ('Trong nhà','Phòng máy lạnh tầng 1'),
 ('Sân vườn','Khu ngoài trời có cây xanh'),
 ('Phòng VIP','Phòng riêng');

INSERT INTO ban (ten_ban, ma_khu_vuc, suc_chua, vi_tri_x, vi_tri_y) VALUES
 ('A1',1,2,20,20),('A2',1,2,120,20),('A3',1,4,220,20),('A4',1,4,320,20),('A5',1,6,20,120),
 ('B1',2,2,20,20),('B2',2,4,120,20),('B3',2,4,220,20),('B4',2,8,320,20),
 ('V1',3,10,20,20),('V2',3,12,220,20);

INSERT INTO khach_hang (ho_ten, so_dien_thoai, email) VALUES
 ('Nguyễn Văn An','0901234567','an@example.com'),
 ('Trần Thị Bình','0912345678','binh@example.com');

INSERT INTO nhan_vien (ten_dang_nhap, mat_khau_hash, ho_ten, vai_tro) VALUES
 ('admin','pbkdf2:sha256:1000000$q3PGS5cYg4EJyFks$961d3aad53541ec821543f2a9ba7913fac184b2c1f2ef6318587b2d564274941','Quản lý nhà hàng','QUAN_LY'),
 ('nhanvien','pbkdf2:sha256:1000000$VEvRq4NYXzjdMBHb$60f0bab782db65c744e78b74abeec03a31e0ef6ddec4720a4ecd698fa69de1d5','Nhân viên phục vụ','NHAN_VIEN');
