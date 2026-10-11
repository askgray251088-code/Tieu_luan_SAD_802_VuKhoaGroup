import os

DB_CONFIG = {
    "host": os.getenv("DATBAN_HOST", "127.0.0.1"),
    "port": int(os.getenv("DATBAN_PORT", "3306")),
    "user": os.getenv("DATBAN_USER", "booking"),
    "password": os.getenv("DATBAN_PASSWORD", "booking123"),
    "database": os.getenv("DATBAN_DB", "datban"),
}

# Business rules (xem docs/01_phan_tich.md)
OPEN_HOUR = 10            # BR01 giờ mở cửa
CLOSE_HOUR = 22           # BR01 giờ đóng cửa
DURATION_MIN = 90         # BR02 thời lượng một lượt đặt
BUFFER_MIN = 15           # BR03 thời gian dọn bàn giữa 2 lượt
MIN_ADVANCE_MIN = 60      # BR04 đặt trước tối thiểu
MAX_ADVANCE_DAYS = 30     # BR04 đặt trước tối đa
CANCEL_BEFORE_MIN = 120   # BR06 chỉ đổi/hủy trước giờ đặt tối thiểu
CHECKIN_EARLY_MIN = 15    # BR07 check-in sớm nhất
CHECKIN_LATE_MIN = 15     # BR07 check-in muộn nhất (quá hạn -> vắng mặt)
MAX_PARTY = 20            # BR05
