"""Pytest configuration: test database + TestClient fixtures.

Sets DATABASE_URL to a temp SQLite file before test modules import the app,
so the app config (loaded via lru_cache) picks up the test database.
Tables are created once in pytest_configure; TestClient does not re-create
them (avoids SQLite write-lock conflicts with the app startup event).
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

_TEST_DB_PATH = None


def pytest_configure(config):
    global _TEST_DB_PATH
    _TEST_DB_PATH = tempfile.mktemp(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
    os.environ["APP_ENV"] = "testing"
    os.environ["DEBUG"] = "true"
    # Set very high rate limits for tests so normal ingestion tests aren't
    # blocked by rate-limiter state from other tests.
    os.environ["RATE_LIMIT_INGEST"] = "10000"
    os.environ["RATE_LIMIT_ANALYZE"] = "10000"
    os.environ["RATE_LIMIT_CHAT"] = "10000"
    os.environ["RATE_LIMIT_DEFAULT"] = "10000"
    os.environ["RATE_LIMIT_HEALTH"] = "10000"

    # Clear cached settings so app.config reloads with test env vars.
    import app.config as config_module

    config_module.get_settings.cache_clear()

    # Create tables once before any test imports the app.
    from app.database.base import Base, engine

    Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def clean_db(client):
    """Delete all documents and analyses before/after each test for isolation."""
    from app.database.base import SessionLocal
    from app.models.analysis import Analysis
    from app.models.document import Document

    db = SessionLocal()
    try:
        db.query(Analysis).delete()
        db.query(Document).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    yield
    db = SessionLocal()
    try:
        db.query(Analysis).delete()
        db.query(Document).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_database():
    yield
    try:
        os.remove(_TEST_DB_PATH)
    except OSError:
        pass
