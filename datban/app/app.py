import io
from datetime import datetime, date

import qrcode
import qrcode.image.svg
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from . import services as S
from .db import get_conn

app = Flask(__name__)
app.secret_key = "dev-only-change-me"

TRANG_THAI = {"DA_XAC_NHAN": "Đã xác nhận", "DA_CHECK_IN": "Đã check-in", "HOAN_THANH": "Hoàn thành",
              "DA_HUY": "Đã hủy", "VANG_MAT": "Vắng mặt"}
app.jinja_env.globals["TT"] = TRANG_THAI


def db():
    return get_conn()


def qr_svg(text):
    img = qrcode.make(text, image_factory=qrcode.image.svg.SvgPathImage, box_size=8)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue().decode()


def parse_dt(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M")


# ---------- khách hàng ----------
@app.route("/")
def index():
    conn = db()
    areas = S.list_areas(conn)
    conn.close()
    return render_template("index.html", areas=areas)


@app.route("/api/availability")
def api_availability():
    conn = db()
    try:
        start, party = parse_dt(request.args["start"]), int(request.args["party"])
        tables = S.find_available_tables(conn, start, party, request.args.get("area") or None)
        return jsonify(tables)
    except (KeyError, ValueError):
        return jsonify([])
    finally:
        conn.close()


@app.route("/dat-ban", methods=["POST"])
def dat_ban():
    f = request.form
    conn = db()
    try:
        r = S.create_reservation(conn, f["ho_ten"], f["sdt"], parse_dt(f["start"]), int(f["party"]),
                                 email=f.get("email") or None, ma_ban=f.get("ma_ban") or None,
                                 area_id=f.get("area") or None, ghi_chu=f.get("ghi_chu") or None)
        return redirect(url_for("xac_nhan", code=r["ma_xac_nhan"]))
    except (S.BookingError, ValueError) as e:
        flash(str(e) if isinstance(e, S.BookingError) else "Dữ liệu nhập chưa hợp lệ", "loi")
        return redirect(url_for("index"))
    finally:
        conn.close()


@app.route("/xac-nhan/<code>")
def xac_nhan(code):
    conn = db()
    try:
        r = S.get_reservation(conn, code)
    except S.BookingError as e:
        flash(str(e), "loi")
        return redirect(url_for("tra_cuu"))
    finally:
        conn.close()
    return render_template("xac_nhan.html", r=r, qr=qr_svg(url_for("check_in_page", code=r["ma_xac_nhan"], _external=True)))


@app.route("/tra-cuu", methods=["GET", "POST"])
def tra_cuu():
    ds, r = [], None
    if request.method == "POST":
        conn = db()
        q = request.form["q"].strip()
        try:
            if q.startswith("0"):
                ds = S.find_by_phone(conn, q)
                if not ds:
                    flash("Không có lượt đặt nào cho số điện thoại này", "loi")
            else:
                return redirect(url_for("xac_nhan", code=q))
        finally:
            conn.close()
    return render_template("tra_cuu.html", ds=ds)


@app.route("/huy/<code>", methods=["POST"])
def huy(code):
    conn = db()
    try:
        S.cancel_reservation(conn, code)
        flash("Đã hủy đặt bàn", "ok")
    except S.BookingError as e:
        flash(str(e), "loi")
    finally:
        conn.close()
    return redirect(url_for("xac_nhan", code=code))


@app.route("/doi/<code>", methods=["POST"])
def doi(code):
    f = request.form
    conn = db()
    try:
        S.modify_reservation(conn, code, new_start=parse_dt(f["start"]), new_party=int(f["party"]))
        flash("Đã cập nhật lượt đặt", "ok")
    except (S.BookingError, ValueError) as e:
        flash(str(e) if isinstance(e, S.BookingError) else "Dữ liệu nhập chưa hợp lệ", "loi")
    finally:
        conn.close()
    return redirect(url_for("xac_nhan", code=code))


# ---------- nhân viên ----------
@app.route("/nhan-vien")
def nhan_vien():
    conn = db()
    S.mark_no_shows(conn)
    day = request.args.get("ngay") or date.today().isoformat()
    ds = S.guest_list(conn, day)
    conn.close()
    return render_template("nhan_vien.html", ds=ds, day=day)


@app.route("/api/so-do-ban")
def api_so_do_ban():
    conn = db()
    at = parse_dt(request.args["at"]) if request.args.get("at") else datetime.now()
    tables = S.table_status_map(conn, at)
    conn.close()
    for t in tables:
        d = t["dat_ban"]
        if d:
            d["thoi_gian_bat_dau"] = d["thoi_gian_bat_dau"].strftime("%H:%M")
            d["thoi_gian_ket_thuc"] = d["thoi_gian_ket_thuc"].strftime("%H:%M")
    return jsonify(tables)


@app.route("/check-in/<code>", methods=["GET", "POST"])
def check_in_page(code):
    """Trang đích của mã QR: nhân viên quét, bấm xác nhận để check-in."""
    conn = db()
    try:
        if request.method == "POST":
            action = request.form.get("action")
            try:
                if action == "hoan_thanh":
                    S.complete(conn, code)
                    flash("Đã hoàn thành lượt đặt, bàn được giải phóng", "ok")
                else:
                    S.check_in(conn, code)
                    flash("Check-in thành công", "ok")
            except S.BookingError as e:
                flash(str(e), "loi")
            return redirect(url_for("check_in_page", code=code))
        r = S.get_reservation(conn, code)
    except S.BookingError as e:
        flash(str(e), "loi")
        return redirect(url_for("nhan_vien"))
    finally:
        conn.close()
    return render_template("check_in.html", r=r)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
