# Kế hoạch & phân công – Đề tài 7: Hệ thống đặt bàn nhà hàng

**Quy trình 6 bước:** 1) Phân tích yêu cầu → 2) Thiết kế → 3) Lập trình → 4) Kiểm thử → 5) Triển khai → 6) Bảo trì.
(Bước 4–6 theo vòng đời phần mềm chuẩn; có thể đổi tên cho khớp giáo trình của lớp.)

## Vai trò

| TV | Vai trò | Phụ trách chính |
|----|---------|-----------------|
| TV1 | Trưởng nhóm + Phân tích nghiệp vụ (BA) | Business rules, SRS, Use Case, quản lý tiến độ, báo cáo |
| TV2 | Thiết kế hệ thống + CSDL | ERD, Class, Sequence, Activity, schema MySQL |
| TV3 | Lập trình backend | Python (tầng nghiệp vụ, kết nối MySQL, API Flask) |
| TV4 | Giao diện + Kiểm thử (QA) | UI prototype, giao diện web, test case, triển khai |

## Công việc theo từng bước

### Bước 1 – Phân tích đặc tả yêu cầu (Tuần 1)
| TV | Công việc | Sản phẩm |
|----|-----------|----------|
| TV1 | Đọc đặc tả (Input/Processing/Output), phỏng vấn giả lập, viết Business rules BR01–BR09, viết SRS (yêu cầu chức năng + phi chức năng) | `01_phan_tich.md` §1–3 |
| TV2 | Xác định thực thể, thuộc tính, quan hệ sơ bộ; vẽ Use Case | `01_phan_tich.md` §4 |
| TV3 | Xác định công nghệ (Python/Flask/MySQL), rủi ro kỹ thuật (đặt trùng bàn, đồng thời) | `01_phan_tich.md` §6 |
| TV4 | Tạo user story và tiêu chí chấp nhận cho từng use case | `01_phan_tich.md` §5 |

### Bước 2 – Thiết kế (Tuần 2)
| TV | Công việc | Sản phẩm |
|----|-----------|----------|
| TV1 | Duyệt thiết kế đối chiếu SRS (bảng truy vết yêu cầu → thiết kế) | `02_thiet_ke.md` §6 |
| TV2 | ERD, Class diagram, Sequence (đặt bàn, check-in), Activity (đặt bàn), `schema.sql` | `02_thiet_ke.md` §1–4, `database/` |
| TV3 | Kiến trúc 3 tầng, thiết kế API/route | `02_thiet_ke.md` §5 |
| TV4 | UI prototype 4 màn hình (đặt bàn, xác nhận + QR, tra cứu, sơ đồ bàn nhân viên) | `02_thiet_ke.md` §7 |

### Bước 3 – Chuyển đổi: Lập trình / Implementation (Tuần 3–4)
| TV | Công việc | Sản phẩm |
|----|-----------|----------|
| TV1 | Theo dõi tiến độ, review code theo checklist business rules | biên bản review |
| TV2 | Tạo CSDL MySQL, dữ liệu mẫu, index, ràng buộc | `database/schema.sql`, `seed.sql` |
| TV3 | `services.py` (đặt/đổi/hủy/check-in), `db.py`, `app.py` | `app/` |
| TV4 | Templates HTML, CSS, JS sơ đồ bàn tương tác, QR check-in | `app/templates`, `static` |

### Bước 4 – Kiểm thử (Tuần 5)
| TV | Công việc | Sản phẩm |
|----|-----------|----------|
| TV1 | Lập ma trận truy vết yêu cầu ↔ test case | `04_kiem_thu.md` |
| TV2 | Kiểm thử CSDL (ràng buộc, khóa ngoại, đặt trùng) | test DB |
| TV3 | Unit test tầng nghiệp vụ (pytest) | `tests/test_booking.py` |
| TV4 | Test giao diện/luồng web, ghi lỗi và theo dõi sửa | `tests/test_web.py` |

### Bước 5 – Triển khai (Tuần 6)
| TV | Công việc | Sản phẩm |
|----|-----------|----------|
| TV1 | Hướng dẫn sử dụng, bàn giao, demo | `README.md` |
| TV2 | Cài đặt MySQL, tạo user, sao lưu | `05_trien_khai_bao_tri.md` |
| TV3 | Đóng gói, biến môi trường, chạy bằng gunicorn | `05_trien_khai_bao_tri.md` |
| TV4 | Kiểm tra nghiệm thu trên môi trường thật | biên bản nghiệm thu |

### Bước 6 – Bảo trì (sau bàn giao)
| TV | Công việc |
|----|-----------|
| TV1 | Thu thập phản hồi, quản lý yêu cầu thay đổi |
| TV2 | Tối ưu truy vấn, sao lưu định kỳ, dọn nhật ký |
| TV3 | Sửa lỗi, mở rộng (đặt cọc, thông báo SMS/email, đăng nhập nhân viên) |
| TV4 | Kiểm thử hồi quy, cập nhật giao diện |
