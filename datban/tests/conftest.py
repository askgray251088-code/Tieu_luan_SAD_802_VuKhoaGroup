import subprocess, pathlib, pytest
from app.db import get_conn

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture()
def conn():
    """Mỗi test dùng CSDL test sạch (datban_test) nạp từ schema.sql + seed.sql."""
    schema = (ROOT / "database/schema.sql").read_text().replace("datban", "datban_test")
    seed = (ROOT / "database/seed.sql").read_text()
    subprocess.run(["mysql", "-uroot"], input=schema.encode(), check=True)
    subprocess.run(["mysql", "-uroot", "datban_test"], input=seed.encode(), check=True)
    c = get_conn(database="datban_test")
    yield c
    c.close()
