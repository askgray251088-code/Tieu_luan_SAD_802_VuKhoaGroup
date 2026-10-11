import mysql.connector
from contextlib import contextmanager
from .config import DB_CONFIG


def get_conn(**overrides):
    cfg = {**DB_CONFIG, **overrides}
    conn = mysql.connector.connect(**cfg, charset="utf8mb4", autocommit=True)
    return conn


@contextmanager
def transaction(conn):
    """Giao dịch tường minh: commit nếu OK, rollback nếu có lỗi."""
    cur = conn.cursor()
    cur.execute("START TRANSACTION")
    try:
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def query(conn, sql, params=(), one=False):
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    if one:
        return rows[0] if rows else None
    return rows


def execute(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    last = cur.lastrowid
    cur.close()
    return last
