"""
In-memory cache for UI inspiration results.
Keyed by normalized query string to avoid redundant API calls.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Thread-safe, TTL-aware in-memory cache."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        """
        Args:
            ttl_seconds: Time-to-live for each cache entry. Defaults to 1 hour.
        """
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def get(self, key: str) -> Any | None:
        """Return cached value for *key*, or ``None`` if missing / expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                logger.debug("Cache entry expired for key=%r", key)
                return None
            logger.debug("Cache hit for key=%r", key)
            return value

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key* with the configured TTL."""
        with self._lock:
            self._store[key] = (value, time.monotonic() + self._ttl)
            logger.debug("Cache set for key=%r (ttl=%ds)", key, self._ttl)

    def clear(self) -> None:
        """Evict all entries (useful for testing)."""
        with self._lock:
            self._store.clear()
            logger.debug("Cache cleared")

    @property
    def size(self) -> int:
        """Current number of live entries (expired entries not counted)."""
        now = time.monotonic()
        with self._lock:
            return sum(1 for _, (_, exp) in self._store.items() if exp > now)


# Module-level singleton shared across the server process.
cache = InMemoryCache(ttl_seconds=3600)
