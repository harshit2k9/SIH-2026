import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings
import time
import json
from typing import Optional
import logging
import asyncio

# PostgreSQL Synchronous SQLAlchemy URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL_COMPUTED

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}  # Fails after 2s instead of hanging
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# Async PostgreSQL connection pool configuration
_pool: asyncpg.Pool | None = None

async def init_db_pool(max_retries: int = 5, delay: float = 2.0) -> None:
    global _pool
    for attempt in range(1, max_retries + 1):
        try:                   
            _pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL_COMPUTED,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                command_timeout=settings.DB_COMMAND_TIMEOUT,
                max_inactive_connection_lifetime=settings.DB_MAX_INACTIVE_LIFETIME,
                statement_cache_size=settings.DB_STATEMENT_CACHE_SIZE,
                server_settings={"statement_timeout": "15000"},
            )
            logging.getLogger(__name__).info(
                f"✅ Database pool initialized successfully (attempt {attempt})"
            )
            return
        except Exception as e:
            if attempt == max_retries:
                logging.getLogger(__name__).error(
                    f"❌ Failed to connect to database after {max_retries} attempts: {e}"
                )
                raise
            logging.getLogger(__name__).warning(
                f"⚠️ Database connection attempt {attempt}/{max_retries} failed: {e}. "
                f"Retrying in {delay}s..."
            )
            
            await asyncio.sleep(delay)


async def close_db_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized — did startup event run?")
    return _pool
