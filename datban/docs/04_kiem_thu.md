# Bước 4 – Kiểm thử

Chạy: `python -m pytest tests -v` (tự tạo CSDL `datban_test`). Kết quả lần chạy cuối: **18/18 đạt**.

## Ma trận truy vết
| Yêu cầu | Test |
|---------|------|
| BR02, BR05, FR02, FR05 | `test_dat_ban_thanh_cong_chon_ban_vua_nhat` |
| BR03, NFR01 | `test_khong_dat_trung_ban_cung_khung_gio`, `test_dem_don_ban_15_phut` |
| BR05 | `test_het_ban_cho_nhom_dong` |
| BR01, BR04, BR05, BR08 | `test_validate_dau_vao` (7 trường hợp) |
| BR06, FR03 | `test_doi_gio_va_tu_doi_ban_khi_can`, `test_huy_va_gioi_han_thoi_gian` |
| BR07, FR06 | `test_checkin_cua_so_thoi_gian` |
| FR07, FR09 | `test_vang_mat_va_so_do_ban` |
| BR08 | `test_khach_cu_khong_bi_nhan_doi` |
| FR01–FR04, FR07 (web) | `test_luong_dat_ban_tra_cuu_check_in`, `test_loi_nghiep_vu_hien_thi` |

## Kết quả chi tiết
```
test_booking.py::test_dat_ban_thanh_cong_chon_ban_vua_nhat PASSED
test_booking.py::test_khong_dat_trung_ban_cung_khung_gio PASSED
test_booking.py::test_dem_don_ban_15_phut PASSED
test_booking.py::test_het_ban_cho_nhom_dong PASSED
test_booking.py::test_validate_dau_vao[start0-2-0900000001] PASSED
test_booking.py::test_validate_dau_vao[start1-2-0900000001] PASSED
test_booking.py::test_validate_dau_vao[start2-2-0900000001] PASSED
test_booking.py::test_validate_dau_vao[start3-2-0900000001] PASSED
test_booking.py::test_validate_dau_vao[start4-0-0900000001] PASSED
test_booking.py::test_validate_dau_vao[start5-25-0900000001] PASSED
test_booking.py::test_validate_dau_vao[start6-2-12345] PASSED
test_booking.py::test_doi_gio_va_tu_doi_ban_khi_can PASSED
test_booking.py::test_huy_va_gioi_han_thoi_gian PASSED
test_booking.py::test_checkin_cua_so_thoi_gian PASSED
test_booking.py::test_vang_mat_va_so_do_ban PASSED
test_booking.py::test_khach_cu_khong_bi_nhan_doi PASSED
test_web.py::test_luong_dat_ban_tra_cuu_check_in PASSED
test_web.py::test_loi_nghiep_vu_hien_thi PASSED
```

## Lỗi đã gặp khi kiểm thử
- Tên khu vực bị lỗi font khi nạp SQL bằng client mặc định → thêm `SET NAMES utf8mb4` vào `schema.sql`/`seed.sql`.
- Một test viết sai kỳ vọng (lượt 20:45 vượt giờ đóng cửa) → sửa test sang khung giờ trưa; code đúng.
