from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# pool_pre_ping checks each pooled connection before use,
# so connections dropped by a DB restart are replaced transparently.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one DB session per request."""
    with SessionLocal() as session:
        yield session
