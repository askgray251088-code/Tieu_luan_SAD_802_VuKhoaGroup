"""Fixture kiểm thử: mỗi test dùng CSDL sạch `datban_test` được nạp lại từ schema.sql + seed.sql.
*** THAY (nếu cần): tài khoản MySQL có quyền tạo CSDL để chạy kiểm thử. Mặc định root, không mật khẩu.
***   Đặt biến môi trường:  DATBAN_ROOT_USER, DATBAN_ROOT_PASSWORD
"""
import os
import pathlib
import subprocess

import pytest

from app import config
from app.db import get_conn, reset_pool

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROOT_USER = os.getenv("DATBAN_ROOT_USER", "root")          # *** THAY nếu tài khoản quản trị MySQL của bạn khác
ROOT_PASSWORD = os.getenv("DATBAN_ROOT_PASSWORD", "")      # *** THAY: mật khẩu tài khoản quản trị MySQL


def _mysql(sql, db=None):
    cmd = ["mysql", "-h", config.DB_CONFIG["host"], "-P", str(config.DB_CONFIG["port"]), "-u", ROOT_USER,
           "--default-character-set=utf8mb4"]
    if ROOT_PASSWORD:
        cmd.append(f"-p{ROOT_PASSWORD}")
    if db:
        cmd.append(db)
    subprocess.run(cmd, input=sql.encode(), check=True)


@pytest.fixture()
def conn():
    _mysql((ROOT / "database/schema.sql").read_text(encoding="utf8").replace("datban", "datban_test"))
    _mysql((ROOT / "database/seed.sql").read_text(encoding="utf8"), db="datban_test")
    c = get_conn(database="datban_test")
    yield c
    c.close()


@pytest.fixture()
def client(conn, monkeypatch):
    """Flask test client trỏ vào CSDL test; đã có sẵn CSRF token = 'tok'."""
    from app import app as webapp
    monkeypatch.setitem(config.DB_CONFIG, "database", "datban_test")
    reset_pool()
    webapp._hits.clear()
    webapp.app.config["TESTING"] = True
    c = webapp.app.test_client()
    with c.session_transaction() as s:
        s["csrf"] = "tok"
    yield c
    reset_pool()
