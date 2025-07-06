"""Redis caching implementation."""

import json
import logging
from datetime import timedelta
from typing import Any, Optional

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache implementation."""

    def __init__(self, redis_url: str):
        """Initialize Redis cache."""
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if not self._client:
            self._client = redis.from_url(self.redis_url)
            await self._client.ping()
            logger.info("Connected to Redis cache")

    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Disconnected from Redis cache")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._client:
            await self.connect()

        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> bool:
        """Set value in cache."""
        if not self._client:
            await self.connect()

        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                return await self._client.setex(key, ttl, serialized)
            else:
                return await self._client.set(key, serialized)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._client:
            await self.connect()

        try:
            return bool(await self._client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._client:
            await self.connect()

        try:
            return bool(await self._client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
