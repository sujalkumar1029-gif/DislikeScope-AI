import pytest
import tempfile
from pathlib import Path
from starlette.testclient import TestClient
from backend import config
from backend.database import init_db


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Use a temporary SQLite database for all tests to ensure isolation."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db_path = Path(tmp.name)

    monkeypatch.setattr(config, "DATABASE_PATH", test_db_path)
    init_db()

    yield test_db_path

    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture
def client():
    from backend.main import app
    with TestClient(app) as c:
        yield c
