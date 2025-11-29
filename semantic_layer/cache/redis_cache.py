"""Redis cache implementation."""

import json
from typing import Any, Optional

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from semantic_layer.cache.base import BaseCache
from semantic_layer.exceptions import ExecutionError


class RedisCache(BaseCache):
    """Redis cache implementation."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize Redis cache."""
        if not REDIS_AVAILABLE:
            raise ExecutionError(
                "Redis is not available. Install with: pip install redis[hiredis]"
            )
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        if self._client is None:
            self._client = await redis.from_url(self.redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self._client is None:
            await self.connect()
        
        value = await self._client.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        if self._client is None:
            await self.connect()
        
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if ttl:
            await self._client.setex(key, ttl, serialized)
        else:
            await self._client.set(key, serialized)

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if self._client is None:
            await self.connect()
        
        await self._client.delete(key)

    async def clear(self) -> None:
        """Clear all cache entries."""
        if self._client is None:
            await self.connect()
        
        await self._client.flushdb()

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if self._client is None:
            await self.connect()
        
        return bool(await self._client.exists(key))

