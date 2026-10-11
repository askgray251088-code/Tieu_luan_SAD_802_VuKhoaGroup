"""Kiểm thử luồng web end-to-end bằng Flask test client trên CSDL test."""
from datetime import datetime, timedelta
import re
import pytest
from app import app as webapp
from app import config


@pytest.fixture()
def client(conn, monkeypatch):
    monkeypatch.setitem(config.DB_CONFIG, "database", "datban_test")
    webapp.app.config["TESTING"] = True
    return webapp.app.test_client()


def next_slot(hour=12):
    d = datetime.now() + timedelta(days=3)
    return d.replace(hour=hour, minute=0, second=0, microsecond=0)


def test_luong_dat_ban_tra_cuu_check_in(client):
    start = next_slot().strftime("%Y-%m-%dT%H:%M")
    # tìm bàn trống
    t = client.get(f"/api/availability?start={start}&party=3").get_json()
    assert t and t[0]["suc_chua"] >= 3
    # đặt bàn
    r = client.post("/dat-ban", data={"ho_ten": "Phạm Web", "sdt": "0933333333", "start": start, "party": "3"})
    assert r.status_code == 302
    code = r.headers["Location"].rsplit("/", 1)[1]
    page = client.get(f"/xac-nhan/{code}").get_data(as_text=True)
    assert "Phạm Web" in page and "<svg" in page            # có mã QR
    # tra cứu theo sđt
    assert code in client.post("/tra-cuu", data={"q": "0933333333"}).get_data(as_text=True)
    # check-in quá sớm -> bị từ chối (3 ngày nữa mới đến giờ)
    client.post(f"/check-in/{code}", data={"action": "check_in"})
    assert "Chưa đến giờ check-in" in client.get(f"/check-in/{code}").get_data(as_text=True)
    # sơ đồ bàn
    sodo = client.get("/api/so-do-ban?at=" + start).get_json()
    assert any(x["trang_thai"] == "DA_DAT" for x in sodo)
    # hủy
    client.post(f"/huy/{code}")
    assert "Đã hủy" in client.get(f"/xac-nhan/{code}").get_data(as_text=True)


def test_loi_nghiep_vu_hien_thi(client):
    r = client.post("/dat-ban", data={"ho_ten": "A", "sdt": "123", "start": next_slot().strftime("%Y-%m-%dT%H:%M"), "party": "2"},
                    follow_redirects=True)
    assert "Số điện thoại không hợp lệ" in r.get_data(as_text=True)
