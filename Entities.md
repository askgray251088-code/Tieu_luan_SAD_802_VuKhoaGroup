1. Xác định các đối tượng chính (Entities)

Từ đặc tả: "Khách hàng; bàn; khu vực; thời gian; số người; trạng thái bàn"

5 thực thể cốt lõi:
|#|	Thực thể |	Vai trò	| Thuộc tính chính |
| :--- | :--- | :--- | :--- | 
|1|	Khách hàng |	Người đặt bàn |	ma_khach, ho_ten, so_dien_thoai, email |
|2|	Khu vực	Phân loại không gian |	ma_khu_vuc, ten_khu_vuc, mo_ta |
|3|	Bàn	Đối tượng được đặt |	ma_ban, ten_ban, suc_chua, vi_tri_x/y, bao_tri, ma_khu_vuc |
|4|	Đặt bàn	Giao dịch trung | tâm	ma_dat_ban, ma_xac_nhan, thoi_gian_bat_dau/ket_thuc, so_nguoi, trang_thai, gio_check_in |
|5|	Nhật ký |	Audit trail |	ma_nhat_ky, hanh_dong, chi_tiet, thoi_gian |
