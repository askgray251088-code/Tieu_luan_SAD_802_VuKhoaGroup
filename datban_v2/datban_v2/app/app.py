"""TẦNG GIAO DIỆN WEB (Flask). Không chứa business rule - chỉ gọi app/services.py."""
import io
import secrets
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from datetime import date, datetime
from functools import wraps

import qrcode
import qrcode.image.svg
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for

from . import config as C
from . import services as S
from .db import get_conn

app = Flask(__name__)
app.secret_key = C.SECRET_KEY
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

TRANG_THAI = {"DA_XAC_NHAN": "Đã xác nhận", "DA_CHECK_IN": "Đã check-in", "HOAN_THANH": "Hoàn thành",
              "DA_HUY": "Đã hủy", "VANG_MAT": "Vắng mặt"}
app.jinja_env.globals["TT"] = TRANG_THAI
app.jinja_env.globals["csrf_token"] = lambda: session.setdefault("csrf", secrets.token_hex(16))


# ---------------------------- tiện ích ----------------------------
@contextmanager
def db():
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()          # với pool: trả kết nối về pool


def parse_dt(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M")


def qr_svg(text):
    img = qrcode.make(text, image_factory=qrcode.image.svg.SvgPathImage, box_size=8)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue().decode()


def checkin_url(code):
    path = url_for("check_in_page", code=code)
    return (C.BASE_URL + path) if C.BASE_URL else url_for("check_in_page", code=code, _external=True)


def err(e):
    flash(str(e) if isinstance(e, S.BookingError) else "Dữ liệu nhập chưa hợp lệ", "loi")


_hits = defaultdict(deque)


def rate_limited(f):
    """Chống spam: tối đa C.RATE_LIMIT_PER_MIN lần / 60 giây / (IP, route)."""
    @wraps(f)
    def w(*a, **k):
        if request.method == "POST":
            q, now = _hits[(request.remote_addr, request.endpoint)], time.time()
            while q and now - q[0] > 60:
                q.popleft()
            if len(q) >= C.RATE_LIMIT_PER_MIN:
                abort(429)
            q.append(now)
        return f(*a, **k)
    return w


def staff_required(role=None):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            u = session.get("user")
            if not u:
                return redirect(url_for("dang_nhap", next=request.full_path.rstrip("?")))
            if role == "QUAN_LY" and u["vai_tro"] != "QUAN_LY":
                flash("Chức năng này chỉ dành cho Quản lý", "loi")
                return redirect(url_for("nhan_vien"))
            return f(*a, **k)
        return w
    return deco


@app.before_request
def csrf_protect():
    if request.method == "POST" and (not session.get("csrf") or request.form.get("_csrf") != session["csrf"]):
        abort(400, "Phiên làm việc không hợp lệ (CSRF). Hãy tải lại trang rồi thử lại.")


@app.errorhandler(429)
def too_many(_):
    return "Bạn thao tác quá nhanh, vui lòng thử lại sau ít phút.", 429


# ---------------------------- KHÁCH HÀNG ----------------------------
@app.route("/")
def index():
    with db() as conn:
        return render_template("index.html", areas=S.list_areas(conn))


@app.route("/api/availability")                                                 # UC01
def api_availability():
    try:
        start, party = parse_dt(request.args["start"]), int(request.args["party"])
    except (KeyError, ValueError):
        return jsonify([])
    with db() as conn:
        return jsonify(S.find_available_tables(conn, start, party, request.args.get("area") or None))


@app.route("/dat-ban", methods=["POST"])                                        # UC02
@rate_limited
def dat_ban():
    f = request.form
    try:
        with db() as conn:
            r = S.create_reservation(conn, f["ho_ten"], f["sdt"], parse_dt(f["start"]), int(f["party"]),
                                     email=f.get("email") or None, ma_ban=f.get("ma_ban") or None,
                                     area_id=f.get("area") or None, ghi_chu=f.get("ghi_chu") or None)
        return redirect(url_for("xac_nhan", code=r["ma_xac_nhan"]))
    except (S.BookingError, ValueError, KeyError) as e:
        err(e)
        return redirect(url_for("index"))


@app.route("/xac-nhan/<code>")                                                  # UC03
def xac_nhan(code):
    try:
        with db() as conn:
            r = S.get_reservation(conn, code)
    except S.BookingError as e:
        err(e)
        return redirect(url_for("tra_cuu"))
    return render_template("xac_nhan.html", r=r, qr=qr_svg(checkin_url(r["ma_xac_nhan"])))


@app.route("/tra-cuu", methods=["GET", "POST"])                                 # UC03
@rate_limited
def tra_cuu():
    ds = []
    if request.method == "POST":
        q = request.form.get("q", "").strip()
        if q.startswith("0"):
            with db() as conn:
                ds = S.find_by_phone(conn, q)
            if not ds:
                flash("Không có lượt đặt nào cho số điện thoại này", "loi")
        elif q:
            return redirect(url_for("xac_nhan", code=q))
    return render_template("tra_cuu.html", ds=ds)


@app.route("/huy/<code>", methods=["POST"])                                     # UC05
def huy(code):
    try:
        with db() as conn:
            S.cancel_reservation(conn, code)
        flash("Đã hủy đặt bàn", "ok")
    except S.BookingError as e:
        err(e)
    return redirect(url_for("xac_nhan", code=code))


@app.route("/doi/<code>", methods=["POST"])                                     # UC04
def doi(code):
    try:
        with db() as conn:
            S.modify_reservation(conn, code, new_start=parse_dt(request.form["start"]), new_party=int(request.form["party"]))
        flash("Đã cập nhật lượt đặt", "ok")
    except (S.BookingError, ValueError, KeyError) as e:
        err(e)
    return redirect(url_for("xac_nhan", code=code))


# ---------------------------- ĐĂNG NHẬP ----------------------------
@app.route("/dang-nhap", methods=["GET", "POST"])                               # UC06
@rate_limited
def dang_nhap():
    nxt = request.args.get("next", "")
    if request.method == "POST":
        try:
            with db() as conn:
                session["user"] = S.authenticate(conn, request.form.get("username"), request.form.get("password"))
            nxt = request.form.get("next", "")
            return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else url_for("nhan_vien"))
        except S.BookingError as e:
            err(e)
    return render_template("dang_nhap.html", next=nxt)


@app.route("/dang-xuat", methods=["POST"])
def dang_xuat():
    session.pop("user", None)
    return redirect(url_for("index"))


# ---------------------------- NHÂN VIÊN ----------------------------
@app.route("/nhan-vien")                                                        # UC07, UC10
@staff_required()
def nhan_vien():
    day = request.args.get("ngay") or date.today().isoformat()
    with db() as conn:
        S.mark_no_shows(conn)                                                   # UC11 (chạy thêm khi mở trang)
        try:
            ds = S.guest_list(conn, day)
        except ValueError:
            ds, day = [], date.today().isoformat()
    return render_template("nhan_vien.html", ds=ds, day=day)


@app.route("/api/so-do-ban")                                                    # UC07
@staff_required()
def api_so_do_ban():
    try:
        at = parse_dt(request.args["at"]) if request.args.get("at") else datetime.now()
    except ValueError:
        at = datetime.now()
    with db() as conn:
        tables = S.table_status_map(conn, at)
    for t in tables:
        d = t["dat_ban"]
        if d:
            d["thoi_gian_bat_dau"] = d["thoi_gian_bat_dau"].strftime("%H:%M")
            d["thoi_gian_ket_thuc"] = d["thoi_gian_ket_thuc"].strftime("%H:%M")
    return jsonify(tables)


@app.route("/check-in/<code>", methods=["GET", "POST"])                         # UC08, UC09 (trang đích của mã QR)
@staff_required()
def check_in_page(code):
    uid = session["user"]["ma_nhan_vien"]
    try:
        with db() as conn:
            if request.method == "POST":
                try:
                    if request.form.get("action") == "hoan_thanh":
                        S.complete(conn, code, staff_id=uid)
                        flash("Đã hoàn thành lượt đặt, bàn được giải phóng", "ok")
                    else:
                        S.check_in(conn, code, staff_id=uid)
                        flash("Check-in thành công", "ok")
                except S.BookingError as e:
                    err(e)
                return redirect(url_for("check_in_page", code=code))
            r = S.get_reservation(conn, code)
    except S.BookingError as e:
        err(e)
        return redirect(url_for("nhan_vien"))
    return render_template("check_in.html", r=r)


# ---------------------------- QUẢN LÝ ----------------------------
@app.route("/quan-ly/ban")                                                      # UC12
@staff_required("QUAN_LY")
def quan_ly_ban():
    with db() as conn:
        return render_template("quan_ly_ban.html", tables=S.list_tables(conn), areas=S.list_areas(conn))


def _admin_action(fn, ok_msg, back):
    try:
        with db() as conn:
            fn(conn)
        flash(ok_msg, "ok")
    except (S.BookingError, ValueError, KeyError) as e:
        err(e)
    return redirect(url_for(back))


@app.route("/quan-ly/ban/luu", methods=["POST"])
@staff_required("QUAN_LY")
def luu_ban():
    f = request.form
    return _admin_action(lambda c: S.save_table(c, f["ten_ban"], int(f["ma_khu_vuc"]), int(f["suc_chua"]),
                                                int(f.get("x") or 0), int(f.get("y") or 0), f.get("ma_ban") or None),
                         "Đã lưu bàn", "quan_ly_ban")


@app.route("/quan-ly/ban/<int:ma_ban>/bao-tri", methods=["POST"])
@staff_required("QUAN_LY")
def bao_tri(ma_ban):
    return _admin_action(lambda c: S.set_maintenance(c, ma_ban, request.form.get("bat") == "1"),
                         "Đã cập nhật trạng thái bảo trì", "quan_ly_ban")


@app.route("/quan-ly/ban/<int:ma_ban>/xoa", methods=["POST"])
@staff_required("QUAN_LY")
def xoa_ban(ma_ban):
    return _admin_action(lambda c: S.delete_table(c, ma_ban), "Đã xóa bàn", "quan_ly_ban")


@app.route("/quan-ly/khu-vuc/them", methods=["POST"])
@staff_required("QUAN_LY")
def them_khu_vuc():
    return _admin_action(lambda c: S.add_area(c, request.form.get("ten"), request.form.get("mo_ta")),
                         "Đã thêm khu vực", "quan_ly_ban")


@app.route("/quan-ly/khu-vuc/<int:ma_khu_vuc>/xoa", methods=["POST"])
@staff_required("QUAN_LY")
def xoa_khu_vuc(ma_khu_vuc):
    return _admin_action(lambda c: S.delete_area(c, ma_khu_vuc), "Đã xóa khu vực", "quan_ly_ban")


@app.route("/quan-ly/nhan-su")                                                  # UC13
@staff_required("QUAN_LY")
def nhan_su():
    with db() as conn:
        return render_template("nhan_su.html", staff=S.list_staff(conn))


@app.route("/quan-ly/nhan-su/them", methods=["POST"])
@staff_required("QUAN_LY")
def them_nhan_su():
    f = request.form
    return _admin_action(lambda c: S.create_staff(c, f.get("username"), f.get("ho_ten"), f.get("password"),
                                                  f.get("vai_tro", "NHAN_VIEN")), "Đã thêm tài khoản", "nhan_su")


@app.route("/quan-ly/nhan-su/<int:ma_nv>/khoa", methods=["POST"])
@staff_required("QUAN_LY")
def khoa_nhan_su(ma_nv):
    if ma_nv == session["user"]["ma_nhan_vien"] and request.form.get("kich_hoat") != "1":
        flash("Bạn không thể tự khóa tài khoản của mình", "loi")
        return redirect(url_for("nhan_su"))
    return _admin_action(lambda c: S.set_staff_active(c, ma_nv, request.form.get("kich_hoat") == "1"),
                         "Đã cập nhật tài khoản", "nhan_su")


@app.route("/quan-ly/nhan-su/<int:ma_nv>/mat-khau", methods=["POST"])
@staff_required("QUAN_LY")
def doi_mat_khau(ma_nv):
    return _admin_action(lambda c: S.reset_staff_password(c, ma_nv, request.form.get("password")),
                         "Đã đặt lại mật khẩu", "nhan_su")


@app.route("/quan-ly/nhat-ky")                                                  # UC14
@staff_required("QUAN_LY")
def nhat_ky():
    with db() as conn:
        return render_template("nhat_ky.html", logs=S.audit_log(conn))
