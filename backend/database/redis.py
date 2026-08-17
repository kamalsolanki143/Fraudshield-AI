"""
FraudShield AI — Redis Cache Client (Optional)
================================================
Provides an async Redis client for caching frequently-accessed data such as
rate-limit counters and analysis results.

The application functions fully without Redis — all methods degrade gracefully
to no-ops when the connection is unavailable.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_redis_url: Optional[str] = os.getenv("REDIS_URL")
_enabled: bool = False


async def connect_redis() -> None:
    """Attempt to connect to Redis if ``REDIS_URL`` is configured.

    Falls back silently when Redis is unavailable — the application
    continues using MongoDB as the sole data store.
    """
    global _enabled

    if not _redis_url:
        logger.info("REDIS_URL not configured — Redis caching disabled.")
        return

    try:
        # Optional dependency — only import when actually needed
        import redis.asyncio as aioredis  # noqa: F811

        _pool = aioredis.from_url(
            _redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        await _pool.ping()
        _enabled = True
        logger.info("✅ Redis connected at %s", _redis_url)
    except ImportError:
        logger.info("redis[asyncio] package not installed — Redis caching disabled.")
    except Exception as exc:
        logger.warning("Redis connection failed (%s) — caching disabled.", exc)


async def close_redis() -> None:
    """Close the Redis connection pool if active."""
    global _enabled
    _enabled = False
    logger.info("🔌 Redis disconnected")


def is_available() -> bool:
    """Return whether Redis is connected and available for caching."""
    return _enabled
