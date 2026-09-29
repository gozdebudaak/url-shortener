import os

# Point the app at a separate test database *before* app modules are imported,
# so tests never touch local development data.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://app:app@localhost:5432/urlshortener_test",
)

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402

from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402


def _create_database_if_missing(url: str) -> None:
    db_url = make_url(url)
    admin = create_engine(db_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": db_url.database}
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_url.database}"'))
    admin.dispose()


@pytest.fixture(scope="session", autouse=True)
def database() -> None:
    """Create the test DB and apply migrations once per test run."""
    _create_database_if_missing(os.environ["DATABASE_URL"])
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture(autouse=True)
def clean_tables() -> None:
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE links RESTART IDENTITY"))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
