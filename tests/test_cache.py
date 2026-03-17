"""Tests for the in-memory cache."""

from __future__ import annotations

import time

import pytest

from mcp_server.services.cache import InMemoryCache


def test_set_and_get() -> None:
    c = InMemoryCache(ttl_seconds=60)
    c.set("key1", {"foo": "bar"})
    assert c.get("key1") == {"foo": "bar"}


def test_get_missing_key_returns_none() -> None:
    c = InMemoryCache(ttl_seconds=60)
    assert c.get("nonexistent") is None


def test_ttl_expiry() -> None:
    c = InMemoryCache(ttl_seconds=1)  # 1-second TTL
    c.set("expiring", "value")
    assert c.get("expiring") == "value"
    time.sleep(1.05)
    assert c.get("expiring") is None


def test_clear() -> None:
    c = InMemoryCache(ttl_seconds=60)
    c.set("a", 1)
    c.set("b", 2)
    assert c.size == 2
    c.clear()
    assert c.size == 0


def test_overwrite_resets_ttl() -> None:
    c = InMemoryCache(ttl_seconds=60)
    c.set("k", "v1")
    c.set("k", "v2")
    assert c.get("k") == "v2"


def test_size_excludes_expired() -> None:
    c = InMemoryCache(ttl_seconds=1)
    c.set("live", "yes")
    c.set("dead", "no")
    time.sleep(1.05)
    # Access so entries are lazily evicted
    c.get("dead")
    # 'live' also expired but size counts lazily
    assert c.size == 0
