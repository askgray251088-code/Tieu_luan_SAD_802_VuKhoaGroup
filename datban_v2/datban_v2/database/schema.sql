SET NAMES utf8mb4;
-- =====================================================================
-- HỆ THỐNG ĐẶT BÀN NHÀ HÀNG HƯƠNG VIỆT - LƯỢC ĐỒ MYSQL 8
-- Chạy:  mysql -u root -p < database/schema.sql
-- *** LƯU Ý: dòng DROP DATABASE bên dưới sẽ XÓA SẠCH CSDL "datban" cũ.
-- *** Nếu muốn đặt tên CSDL khác: thay "datban" ở 2 dòng DROP/CREATE và USE,
-- ***   đồng thời đổi biến DATBAN_DB (hoặc DB_CONFIG["database"] trong app/config.py).
-- =====================================================================

CREATE DATABASE datban CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE datban;

CREATE TABLE khu_vuc (
  ma_khu_vuc  INT AUTO_INCREMENT PRIMARY KEY,
  ten_khu_vuc VARCHAR(50) NOT NULL UNIQUE,
  mo_ta       VARCHAR(200)
) ENGINE=InnoDB;

CREATE TABLE ban (
  ma_ban     INT AUTO_INCREMENT PRIMARY KEY,
  ten_ban    VARCHAR(20) NOT NULL UNIQUE,
  ma_khu_vuc INT NOT NULL,
  suc_chua   INT NOT NULL,
  vi_tri_x   INT NOT NULL DEFAULT 0,        -- toạ độ trên sơ đồ bàn (px)
  vi_tri_y   INT NOT NULL DEFAULT 0,
  bao_tri    TINYINT(1) NOT NULL DEFAULT 0, -- 1 = đang bảo trì
  FOREIGN KEY (ma_khu_vuc) REFERENCES khu_vuc(ma_khu_vuc),
  CHECK (suc_chua BETWEEN 1 AND 20)
) ENGINE=InnoDB;

CREATE TABLE khach_hang (
  ma_khach      INT AUTO_INCREMENT PRIMARY KEY,
  ho_ten        VARCHAR(100) NOT NULL,
  so_dien_thoai VARCHAR(15)  NOT NULL UNIQUE,   -- khóa định danh khách
  email         VARCHAR(100),
  ngay_tao      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE nhan_vien (
  ma_nhan_vien  INT AUTO_INCREMENT PRIMARY KEY,
  ten_dang_nhap VARCHAR(30)  NOT NULL UNIQUE,
  mat_khau_hash VARCHAR(255) NOT NULL,          -- băm PBKDF2-SHA256 + salt, KHÔNG lưu mật khẩu gốc
  ho_ten        VARCHAR(100) NOT NULL,
  vai_tro       ENUM('NHAN_VIEN','QUAN_LY') NOT NULL DEFAULT 'NHAN_VIEN',
  kich_hoat     TINYINT(1) NOT NULL DEFAULT 1,
  ngay_tao      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE dat_ban (
  ma_dat_ban         INT AUTO_INCREMENT PRIMARY KEY,
  ma_xac_nhan        CHAR(8) NOT NULL UNIQUE,   -- mã xác nhận = nội dung QR
  ma_khach           INT NOT NULL,
  ma_ban             INT NOT NULL,
  thoi_gian_bat_dau  DATETIME NOT NULL,
  thoi_gian_ket_thuc DATETIME NOT NULL,
  so_nguoi           INT NOT NULL,
  ghi_chu            VARCHAR(200),
  trang_thai ENUM('DA_XAC_NHAN','DA_CHECK_IN','HOAN_THANH','DA_HUY','VANG_MAT')
             NOT NULL DEFAULT 'DA_XAC_NHAN',
  ngay_tao           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  gio_check_in       DATETIME NULL,
  FOREIGN KEY (ma_khach) REFERENCES khach_hang(ma_khach),
  FOREIGN KEY (ma_ban)   REFERENCES ban(ma_ban),
  CHECK (thoi_gian_ket_thuc > thoi_gian_bat_dau),
  CHECK (so_nguoi BETWEEN 1 AND 20),
  INDEX idx_ban_thoigian (ma_ban, thoi_gian_bat_dau, thoi_gian_ket_thuc),
  INDEX idx_trangthai_gio (trang_thai, thoi_gian_bat_dau),  -- quét vắng mặt, danh sách khách theo ngày
  INDEX idx_khach (ma_khach)
) ENGINE=InnoDB;

CREATE TABLE nhat_ky_dat_ban (
  ma_nhat_ky   INT AUTO_INCREMENT PRIMARY KEY,
  ma_dat_ban   INT NOT NULL,
  ma_nhan_vien INT NULL,                        -- NULL = khách hoặc hệ thống tự động
  hanh_dong    VARCHAR(30) NOT NULL,            -- TAO / DOI / HUY / CHECK_IN / HOAN_THANH / VANG_MAT
  chi_tiet     VARCHAR(255),
  thoi_gian    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ma_dat_ban)   REFERENCES dat_ban(ma_dat_ban),
  FOREIGN KEY (ma_nhan_vien) REFERENCES nhan_vien(ma_nhan_vien),
  INDEX idx_thoigian (thoi_gian)
) ENGINE=InnoDB;
