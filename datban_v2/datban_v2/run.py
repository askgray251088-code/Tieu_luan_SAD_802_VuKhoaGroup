"""ĐIỂM KHỞI CHẠY WEB.   Chạy:  python run.py
Các thông số (địa chỉ, cổng, debug) nằm trong app/config.py - tìm các dòng có dấu ***."""
import os
import threading
import time

from app import config as C
from app import services as S
from app.app import app
from app.db import get_conn


def scan_no_shows_forever():
    """Luồng nền: cứ mỗi N giây tự đánh dấu 'Vắng mặt' cho lượt quá hạn check-in (UC11)."""
    while True:
        time.sleep(C.NO_SHOW_SCAN_SECONDS)
        try:
            conn = get_conn()
            try:
                n = S.mark_no_shows(conn)
            finally:
                conn.close()
            if n:
                print(f"[scheduler] đã đánh dấu vắng mặt {n} lượt đặt")
        except Exception as e:                                                   # không để luồng nền chết vì lỗi tạm thời
            print("[scheduler] lỗi:", e)


if __name__ == "__main__":
    # khi bật debug, Flask chạy 2 tiến trình; chỉ khởi động luồng nền ở tiến trình chính
    if C.NO_SHOW_SCAN_SECONDS > 0 and (not C.DEBUG or os.environ.get("WERKZEUG_RUN_MAIN") == "true"):
        threading.Thread(target=scan_no_shows_forever, daemon=True).start()
    print(f"Mở trình duyệt: http://{'localhost' if C.WEB_HOST in ('127.0.0.1', '0.0.0.0') else C.WEB_HOST}:{C.WEB_PORT}")
    app.run(host=C.WEB_HOST, port=C.WEB_PORT, debug=C.DEBUG)
