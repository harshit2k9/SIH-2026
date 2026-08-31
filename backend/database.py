from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import asyncpg
from config import settings


DATABASE_URL = "sqlite:///./sih26.db"
_pool: asyncpg.Pool | None = None

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()

async def init_db_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=settings.DB_POOL_MIN_SIZE,
        max_size=settings.DB_POOL_MAX_SIZE,
        command_timeout=settings.DB_COMMAND_TIMEOUT,
        max_inactive_connection_lifetime=settings.DB_MAX_INACTIVE_LIFETIME,
        statement_cache_size=settings.DB_STATEMENT_CACHE_SIZE,
        # server_settings can pin session-level params (timezone, statement_timeout)
        server_settings={"statement_timeout": "15000"},  # 15s hard cap, prevents runaway queries
    )


async def close_db_pool() -> None:
    if _pool is not None:
        await _pool.close()


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized — did startup event run?")
    return _pool
