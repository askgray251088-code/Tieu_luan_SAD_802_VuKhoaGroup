# Bước 3 – Chuyển đổi: Lập trình / Implementation

## Cấu trúc mã nguồn
```
datban/
├── database/schema.sql, seed.sql   # MySQL: 5 bảng + dữ liệu mẫu
├── app/config.py                   # Hằng số business rule (BR01-BR07)
├── app/db.py                       # Kết nối, query, giao dịch
├── app/services.py                 # Toàn bộ nghiệp vụ (không phụ thuộc Flask)
├── app/app.py                      # Route Flask + QR
├── app/templates, static           # Giao diện
├── tests/                          # pytest (nghiệp vụ + web)
└── demo.py                         # Chạy thử luồng trên MySQL
```
## Ánh xạ thiết kế → mã
| Thiết kế | Mã |
|----------|----|
| BR01–BR07 | `config.py` + `_validate_time`, `_require_changeable`, `check_in` |
| Chống đặt trùng (BR03, NFR01) | `create_reservation`: `SELECT ... FOR UPDATE` + `_conflict` trong `transaction()` |
| Xếp bàn vừa nhất (BR05) | `find_available_tables`: `ORDER BY suc_chua` |
| Trạng thái bàn suy ra | `table_status_map` |
| Nhật ký (FR10) | `_log` |

## Quy ước
Tên bảng/cột tiếng Việt không dấu; lỗi nghiệp vụ ném `BookingError` (giao diện hiển thị nguyên văn); hàm nhận tham số `now` để kiểm thử theo thời gian giả lập.
