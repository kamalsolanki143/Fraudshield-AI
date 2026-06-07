"""
Async Redis client singleton for FraudShield.
All operations fail silently — log warning on failure, never crash.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class RedisClient:
    _instance: "RedisClient | None" = None

    UPI_TTL = 3600
    PHONE_TTL = 3600
    USER_TTL = 300
    RATE_LIMIT_TTL = 60

    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.client: aioredis.Redis | None = None

    async def initialize(self) -> None:
        url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.client = aioredis.from_url(url, decode_responses=True)
            await self.client.ping()
            logger.info("Redis connected: %s", url)
        except Exception:
            logger.warning("Redis connection failed — running without cache: %s", url)
            self.client = None

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()
            logger.info("Redis connection closed")

    async def get(self, key: str) -> str | None:
        if self.client is None:
            return None
        try:
            return await self.client.get(key)
        except Exception:
            logger.warning("Redis get failed for key=%s", key)
            return None

    async def set(self, key: str, value: str, ttl: int) -> bool:
        if self.client is None:
            return False
        try:
            await self.client.setex(key, ttl, value)
            return True
        except Exception:
            logger.warning("Redis set failed for key=%s", key)
            return False

    async def delete(self, key: str) -> bool:
        if self.client is None:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception:
            logger.warning("Redis delete failed for key=%s", key)
            return False

    # ── UPI CACHE ─────────────────────────────────────────

    async def get_cached_upi(self, upi_id: str) -> dict | None:
        raw = await self.get(f"upi:{upi_id}")
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    async def set_cached_upi(self, upi_id: str, data: dict) -> bool:
        try:
            return await self.set(f"upi:{upi_id}", json.dumps(data, default=str), self.UPI_TTL)
        except Exception:
            return False

    async def invalidate_upi(self, upi_id: str) -> bool:
        return await self.delete(f"upi:{upi_id}")

    # ── PHONE CACHE ───────────────────────────────────────

    async def get_cached_phone(self, phone: str) -> dict | None:
        raw = await self.get(f"phone:{phone}")
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    async def set_cached_phone(self, phone: str, data: dict) -> bool:
        try:
            return await self.set(f"phone:{phone}", json.dumps(data, default=str), self.PHONE_TTL)
        except Exception:
            return False

    # ── USER CACHE ────────────────────────────────────────

    async def get_cached_user(self, user_id: str) -> dict | None:
        raw = await self.get(f"user:{user_id}")
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    async def set_cached_user(self, user_id: str, data: dict) -> bool:
        try:
            return await self.set(f"user:{user_id}", json.dumps(data, default=str), self.USER_TTL)
        except Exception:
            return False

    async def invalidate_user(self, user_id: str) -> bool:
        return await self.delete(f"user:{user_id}")

    # ── RATE LIMIT ────────────────────────────────────────

    async def check_rate_limit(self, user_id: str, action: str, limit: int) -> bool:
        if self.client is None:
            return True
        key = f"ratelimit:{user_id}:{action}"
        try:
            current = await self.client.get(key)
            if current is None:
                await self.client.setex(key, self.RATE_LIMIT_TTL, 1)
                return True
            count = int(current)
            if count >= limit:
                return False
            await self.client.incr(key)
            return True
        except Exception:
            logger.warning("Rate limit check failed for %s:%s", user_id, action)
            return True
