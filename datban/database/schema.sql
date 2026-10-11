SET NAMES utf8mb4;
-- Hệ thống đặt bàn nhà hàng - Lược đồ MySQL 8
DROP DATABASE IF EXISTS datban;
CREATE DATABASE datban CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE datban;

CREATE TABLE khu_vuc (
  ma_khu_vuc INT AUTO_INCREMENT PRIMARY KEY,
  ten_khu_vuc VARCHAR(50) NOT NULL UNIQUE,
  mo_ta VARCHAR(200)
);

CREATE TABLE ban (
  ma_ban INT AUTO_INCREMENT PRIMARY KEY,
  ten_ban VARCHAR(20) NOT NULL UNIQUE,
  ma_khu_vuc INT NOT NULL,
  suc_chua INT NOT NULL CHECK (suc_chua BETWEEN 1 AND 20),
  vi_tri_x INT NOT NULL DEFAULT 0,
  vi_tri_y INT NOT NULL DEFAULT 0,
  bao_tri TINYINT(1) NOT NULL DEFAULT 0,
  FOREIGN KEY (ma_khu_vuc) REFERENCES khu_vuc(ma_khu_vuc)
);

CREATE TABLE khach_hang (
  ma_khach INT AUTO_INCREMENT PRIMARY KEY,
  ho_ten VARCHAR(100) NOT NULL,
  so_dien_thoai VARCHAR(15) NOT NULL UNIQUE,
  email VARCHAR(100),
  ngay_tao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dat_ban (
  ma_dat_ban INT AUTO_INCREMENT PRIMARY KEY,
  ma_xac_nhan CHAR(8) NOT NULL UNIQUE,
  ma_khach INT NOT NULL,
  ma_ban INT NOT NULL,
  thoi_gian_bat_dau DATETIME NOT NULL,
  thoi_gian_ket_thuc DATETIME NOT NULL,
  so_nguoi INT NOT NULL CHECK (so_nguoi BETWEEN 1 AND 20),
  ghi_chu VARCHAR(200),
  trang_thai ENUM('DA_XAC_NHAN','DA_CHECK_IN','HOAN_THANH','DA_HUY','VANG_MAT')
             NOT NULL DEFAULT 'DA_XAC_NHAN',
  ngay_tao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  gio_check_in DATETIME NULL,
  FOREIGN KEY (ma_khach) REFERENCES khach_hang(ma_khach),
  FOREIGN KEY (ma_ban) REFERENCES ban(ma_ban),
  CHECK (thoi_gian_ket_thuc > thoi_gian_bat_dau),
  INDEX idx_ban_thoigian (ma_ban, thoi_gian_bat_dau, thoi_gian_ket_thuc),
  INDEX idx_khach (ma_khach)
);

CREATE TABLE nhat_ky_dat_ban (
  ma_nhat_ky INT AUTO_INCREMENT PRIMARY KEY,
  ma_dat_ban INT NOT NULL,
  hanh_dong VARCHAR(30) NOT NULL,
  chi_tiet VARCHAR(255),
  thoi_gian DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ma_dat_ban) REFERENCES dat_ban(ma_dat_ban)
);
