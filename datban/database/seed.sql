SET NAMES utf8mb4;
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
