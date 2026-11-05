"""Kết nối MySQL: dùng connection pool để không phải mở kết nối mới ở mỗi request."""
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling

from . import config

_pool = None


def reset_pool():
    """Hủy pool hiện tại (dùng khi đổi cấu hình, ví dụ trong kiểm thử)."""
    global _pool
    _pool = None


def get_conn(**overrides):
    """Lấy 1 kết nối. conn.close() sẽ TRẢ kết nối về pool (không đóng thật).
    Nếu truyền overrides (vd database='datban_test') thì mở kết nối riêng, không qua pool."""
    global _pool
    if overrides:
        return mysql.connector.connect(**{**config.DB_CONFIG, **overrides}, charset="utf8mb4", autocommit=True)
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(pool_name="datban", pool_size=config.POOL_SIZE,
                                            **config.DB_CONFIG, charset="utf8mb4", autocommit=True)
    return _pool.get_connection()


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


def execute_many(conn, sql, rows):
    cur = conn.cursor()
    cur.executemany(sql, rows)
    cur.close()
