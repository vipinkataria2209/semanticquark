"""In-memory cache implementation."""

import time
from typing import Any, Optional

from semantic_layer.cache.base import BaseCache


class CacheEntry:
    """Cache entry with expiration."""

    def __init__(self, value: Any, expires_at: Optional[float] = None):
        self.value = value
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class MemoryCache(BaseCache):
    """In-memory cache implementation."""

    def __init__(self):
        """Initialize memory cache."""
        self._cache: dict[str, CacheEntry] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self._cache.get(key)
        if entry is None:
            return None
        
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        expires_at = None
        if ttl:
            expires_at = time.time() + ttl
        
        self._cache[key] = CacheEntry(value, expires_at)

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]

    async def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        entry = self._cache.get(key)
        if entry is None:
            return False
        if entry.is_expired():
            del self._cache[key]
            return False
        return True

