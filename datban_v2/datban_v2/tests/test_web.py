"""Kiểm thử luồng web end-to-end (Flask test client) trên CSDL test."""
from datetime import datetime, timedelta


def post(client, url, **data):
    return client.post(url, data={"_csrf": "tok", **data})


def login(client, u="nhanvien", p="Nhanvien@123"):
    return post(client, "/dang-nhap", username=u, password=p)


def next_slot(hour=12):
    return (datetime.now() + timedelta(days=3)).replace(hour=hour, minute=0, second=0, microsecond=0)


def test_luong_khach_dat_tra_cuu_huy(client):
    start = next_slot().strftime("%Y-%m-%dT%H:%M")
    assert client.get(f"/api/availability?start={start}&party=3").get_json()[0]["suc_chua"] >= 3
    r = post(client, "/dat-ban", ho_ten="Phạm Web", sdt="0933333333", start=start, party="3")
    assert r.status_code == 302
    code = r.headers["Location"].rsplit("/", 1)[1]
    page = client.get(f"/xac-nhan/{code}").get_data(as_text=True)
    assert "Phạm Web" in page and "<svg" in page
    assert code in post(client, "/tra-cuu", q="0933333333").get_data(as_text=True)
    post(client, f"/huy/{code}")
    assert "Đã hủy" in client.get(f"/xac-nhan/{code}").get_data(as_text=True)


def test_loi_nghiep_vu_hien_thi(client):
    r = post(client, "/dat-ban", ho_ten="A", sdt="123", start=next_slot().strftime("%Y-%m-%dT%H:%M"), party="2")
    assert "Số điện thoại không hợp lệ" in client.get(r.headers["Location"]).get_data(as_text=True)


def test_csrf_chan_form_gia_mao(client):
    assert client.post("/dat-ban", data={"ho_ten": "A"}).status_code == 400          # thiếu token
    assert client.post("/dang-nhap", data={"_csrf": "sai"}).status_code == 400


def test_trang_nhan_vien_can_dang_nhap_va_phan_quyen(client):
    assert client.get("/nhan-vien").status_code == 302 and "/dang-nhap" in client.get("/nhan-vien").headers["Location"]
    assert client.get("/api/so-do-ban").status_code == 302
    login(client, "nhanvien", "sai")
    assert client.get("/nhan-vien").status_code == 302                              # đăng nhập sai
    login(client)
    assert client.get("/nhan-vien").status_code == 200
    assert len(client.get("/api/so-do-ban").get_json()) == 11
    assert client.get("/quan-ly/ban").status_code == 302                            # nhân viên không vào được trang quản lý
    assert client.get("/quan-ly/nhat-ky").status_code == 302


def test_quan_ly_thao_tac(client):
    login(client, "admin", "Admin@123")
    assert client.get("/quan-ly/ban").status_code == 200
    post(client, "/quan-ly/ban/luu", ten_ban="Z9", ma_khu_vuc="1", suc_chua="4", x="5", y="5")
    assert "Z9" in client.get("/quan-ly/ban").get_data(as_text=True)
    post(client, "/quan-ly/nhan-su/them", username="moi", ho_ten="Mới", password="abcdef", vai_tro="NHAN_VIEN")
    assert "moi" in client.get("/quan-ly/nhan-su").get_data(as_text=True)
    assert client.get("/quan-ly/nhat-ky").status_code == 200


def test_checkin_qua_web_va_chan_open_redirect(client):
    start = next_slot().strftime("%Y-%m-%dT%H:%M")
    code = post(client, "/dat-ban", ho_ten="K", sdt="0944444444", start=start, party="2").headers["Location"].rsplit("/", 1)[1]
    assert client.get(f"/check-in/{code}").status_code == 302                       # chưa đăng nhập
    r = post(client, "/dang-nhap", username="nhanvien", password="Nhanvien@123", next="//evil.com")
    assert "evil.com" not in r.headers["Location"]
    post(client, f"/check-in/{code}", action="check_in")                             # còn 3 ngày -> bị từ chối
    assert "Chưa đến giờ check-in" in client.get(f"/check-in/{code}").get_data(as_text=True)


def test_gioi_han_toc_do_dang_nhap(client):
    codes = [login(client, "x", "y").status_code for _ in range(12)]
    assert 429 in codes
