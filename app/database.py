"""
asyncpg connection pool — created once at app startup, reused for every request.
Never call asyncpg.connect() per-request: that adds real, measurable latency
(TCP handshake + auth) on every single call.
"""
import asyncpg
from app.config import settings

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
