from sqlalchemy import create_engine

from app.config import settings

# pool_pre_ping checks each pooled connection before use,
# so connections dropped by a DB restart are replaced transparently.
engine = create_engine(settings.database_url, pool_pre_ping=True)
