# database.py
import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

# Sync SQLite configuration for local ORM operations
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Async PostgreSQL connection pool configuration
_pool: asyncpg.Pool | None = None

async def init_db_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=settings.DB_POOL_MIN_SIZE,
        max_size=settings.DB_POOL_MAX_SIZE,
        command_timeout=settings.DB_COMMAND_TIMEOUT,
        max_inactive_connection_lifetime=settings.DB_MAX_INACTIVE_LIFETIME,
        statement_cache_size=settings.DB_STATEMENT_CACHE_SIZE,
        server_settings={"statement_timeout": "15000"},
    )


async def close_db_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized — did startup event run?")
    return _pool