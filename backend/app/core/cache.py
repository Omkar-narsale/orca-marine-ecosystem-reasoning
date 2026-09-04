import time
from typing import Any, Optional, Dict, Tuple

class TTLCache:
    """
    Lightweight in-memory TTL Cache for marine and weather API responses.
    Differentiates short TTL for weather, moderate TTL for ocean forecasts, long TTL for static cadastres.
    """
    def __init__(self):
        self._cache: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        expires_at, value = self._cache[key]
        if time.time() > expires_at:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        expires_at = time.time() + ttl_seconds
        self._cache[key] = (expires_at, value)

    def clear(self) -> None:
        self._cache.clear()

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

# Global cache instance
cache = TTLCache()
