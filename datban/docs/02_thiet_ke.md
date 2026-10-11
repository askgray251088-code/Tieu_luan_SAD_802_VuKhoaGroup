# Bước 2 – Thiết kế

## 1. ERD
```mermaid
erDiagram
  KHU_VUC ||--o{ BAN : "có"
  KHACH_HANG ||--o{ DAT_BAN : "đặt"
  BAN ||--o{ DAT_BAN : "được xếp"
  DAT_BAN ||--o{ NHAT_KY_DAT_BAN : "ghi nhật ký"
  KHU_VUC { int ma_khu_vuc PK
            string ten_khu_vuc }
  BAN { int ma_ban PK
        string ten_ban
        int suc_chua
        int vi_tri_x
        int vi_tri_y
        bool bao_tri
        int ma_khu_vuc FK }
  KHACH_HANG { int ma_khach PK
               string ho_ten
               string so_dien_thoai UK
               string email }
  DAT_BAN { int ma_dat_ban PK
            string ma_xac_nhan UK
            datetime thoi_gian_bat_dau
            datetime thoi_gian_ket_thuc
            int so_nguoi
            enum trang_thai
            datetime gio_check_in
            int ma_khach FK
            int ma_ban FK }
  NHAT_KY_DAT_BAN { int ma_nhat_ky PK
                    string hanh_dong
                    datetime thoi_gian
                    int ma_dat_ban FK }
```
Trạng thái bàn **không lưu cứng**: được suy ra từ các lượt đặt tại thời điểm xem (tránh dữ liệu lệch).

## 2. Class diagram
```mermaid
classDiagram
  class KhachHang { +ma_khach +ho_ten +so_dien_thoai +email }
  class KhuVuc { +ma_khu_vuc +ten_khu_vuc }
  class Ban { +ma_ban +ten_ban +suc_chua +bao_tri }
  class DatBan { +ma_xac_nhan +bat_dau +ket_thuc +so_nguoi +trang_thai }
  class BookingService {
    +find_available_tables()
    +create_reservation()
    +modify_reservation()
    +cancel_reservation()
    +check_in()
    +complete()
    +mark_no_shows()
    +table_status_map()
  }
  KhuVuc "1" --> "*" Ban
  KhachHang "1" --> "*" DatBan
  Ban "1" --> "*" DatBan
  BookingService ..> DatBan
  BookingService ..> Ban
```

## 3. Sequence – Đặt bàn
```mermaid
sequenceDiagram
  actor K as Khách
  participant W as Web (Flask)
  participant S as BookingService
  participant DB as MySQL
  K->>W: Nhập ngày giờ, số người
  W->>S: find_available_tables()
  S->>DB: SELECT bàn không trùng lịch
  DB-->>W: danh sách bàn
  K->>W: Gửi họ tên, SĐT, chọn bàn
  W->>S: create_reservation()
  S->>S: kiểm tra BR01-BR05, BR08
  S->>DB: START TRANSACTION, SELECT ... FOR UPDATE (bàn)
  S->>DB: kiểm tra trùng, INSERT dat_ban + nhật ký
  S->>DB: COMMIT
  S-->>W: lượt đặt + mã xác nhận
  W-->>K: Trang xác nhận + QR
```

## 4. Activity – Đặt bàn
```mermaid
flowchart TD
  A([Bắt đầu]) --> B[Nhập ngày giờ, số người]
  B --> C{Hợp lệ BR01-BR05?}
  C -- Không --> E[Báo lỗi] --> B
  C -- Có --> D{Còn bàn trống?}
  D -- Không --> F[Gợi ý giờ khác] --> B
  D -- Có --> G[Chọn bàn / tự xếp bàn vừa nhất]
  G --> H[Nhập thông tin khách]
  H --> I[Khóa bàn, kiểm tra trùng lần cuối]
  I --> J{Còn trống?}
  J -- Không --> F
  J -- Có --> K[Lưu, sinh mã + QR]
  K --> L([Kết thúc])
```
**Sequence check-in (tóm tắt):** Nhân viên quét QR → `GET /check-in/<mã>` → bấm xác nhận → `check_in()` kiểm tra BR07 → cập nhật `DA_CHECK_IN` + ghi nhật ký.

## 5. Kiến trúc
3 tầng: **Giao diện** (Jinja + JS) → **Nghiệp vụ** (`services.py`, mọi business rule ở đây) → **Dữ liệu** (`db.py` + MySQL). Cấu hình rule tập trung trong `config.py`.

| Route | Chức năng |
|-------|-----------|
| `GET /`, `GET /api/availability` | Form đặt bàn, bàn trống |
| `POST /dat-ban`, `GET /xac-nhan/<mã>` | Đặt bàn, xác nhận + QR |
| `POST /doi/<mã>`, `POST /huy/<mã>` | Đổi / hủy |
| `/tra-cuu` | Tra cứu theo mã hoặc SĐT |
| `/nhan-vien`, `/api/so-do-ban` | Sơ đồ bàn + danh sách khách |
| `/check-in/<mã>` | Trang đích của QR |

## 6. Truy vết yêu cầu → thiết kế
FR01→`find_available_tables`; FR02/FR05→`create_reservation`; FR03→`modify/cancel`; FR04→`/tra-cuu`; FR06→`check_in/complete`; FR07→`table_status_map`; FR08→`guest_list`; FR09→`mark_no_shows`; FR10→bảng `nhat_ky_dat_ban`.

## 7. UI prototype (4 màn hình)
1. **Đặt bàn:** ngày giờ + số người + khu vực → nút bàn trống → họ tên, SĐT → xác nhận.
2. **Xác nhận:** mã, thông tin lượt đặt, mã QR, form đổi/hủy.
3. **Tra cứu:** ô nhập mã/SĐT → bảng lượt đặt.
4. **Nhân viên:** sơ đồ bàn theo khu vực (xanh=trống, vàng=đã đặt, đỏ=đang phục vụ, xám=bảo trì), chọn thời điểm, danh sách khách theo ngày.
(Bản chạy thật nằm trong `app/templates/`.)
