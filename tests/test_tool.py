"""Integration-style tests for the get_ui_inspiration tool."""

from __future__ import annotations

import pytest

from mcp_server.services.cache import InMemoryCache
from mcp_server.tools.ui_inspiration import _normalize_cache_key, get_ui_inspiration


def test_get_ui_inspiration_returns_valid_schema() -> None:
    result = get_ui_inspiration("fintech login mobile")
    required_keys = {
        "query", "type", "style", "platform", "patterns",
        "components", "layout", "design_notes", "references",
        "source", "result_count",
    }
    assert required_keys.issubset(set(result.keys()))


def test_get_ui_inspiration_query_preserved() -> None:
    q = "minimal todo app"
    result = get_ui_inspiration(q)
    assert result["query"] == q


def test_get_ui_inspiration_never_crashes_on_garbage() -> None:
    """Tool must return a valid dict for any input."""
    for garbage in ["", "   ", "🚀🎨💻", "a" * 2000]:
        result = get_ui_inspiration(garbage)
        assert isinstance(result, dict)
        assert "type" in result


def test_get_ui_inspiration_caches_result(monkeypatch: pytest.MonkeyPatch) -> None:
    """Second call should return identical object (from cache), not re-process."""
    import mcp_server.tools.ui_inspiration as mod

    call_count = 0
    original_parse = mod.parse_query  # type: ignore[attr-defined]

    def counting_parse(q: str):  # type: ignore[no-untyped-def]
        nonlocal call_count
        call_count += 1
        return original_parse(q)

    monkeypatch.setattr(mod, "parse_query", counting_parse)
    # Clear cache to start fresh
    mod.cache.clear()

    get_ui_inspiration("saas dashboard")
    get_ui_inspiration("saas dashboard")  # should be cached

    assert call_count == 1, "parse_query should only be called once (second call cached)"


def test_normalize_cache_key_lowercases_and_strips() -> None:
    assert _normalize_cache_key("  Fintech LOGIN  ") == "fintech login"
    assert _normalize_cache_key("a  b   c") == "a b c"
