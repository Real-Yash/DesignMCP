"""Tests for the query parser service."""

from __future__ import annotations

import pytest

from mcp_server.services.parser import parse_query_rule_based


@pytest.mark.parametrize(
    "query,expected_type,expected_style,expected_platform",
    [
        ("fintech login mobile", "login", "fintech", "mobile"),
        ("saas analytics dashboard web", "dashboard", "saas", "web"),
        ("minimal todo app mobile", "todo", "minimal", "mobile"),
        ("ecommerce checkout web", "checkout", "ecommerce", "web"),
        ("social profile screen ios", "profile", "social", "mobile"),
        ("travel search mobile", "search", "travel", "mobile"),
        ("health onboarding mobile", "onboarding", "health", "mobile"),
        ("landing page saas startup web", "landing page", "saas", "web"),
        ("sign in screen fintech", "login", "fintech", "mobile"),  # 'sign in' keyword
        ("register form dark mode", "signup", "dark mode", "mobile"),
    ],
)
def test_parse_query_rule_based(
    query: str,
    expected_type: str,
    expected_style: str,
    expected_platform: str,
) -> None:
    result = parse_query_rule_based(query)
    assert result["type"] == expected_type, f"type mismatch for {query!r}: {result}"
    assert result["style"] == expected_style, f"style mismatch for {query!r}: {result}"
    assert result["platform"] == expected_platform, f"platform mismatch for {query!r}: {result}"


def test_parse_empty_query_returns_defaults() -> None:
    """Completely unknown query should return generic defaults, not crash."""
    result = parse_query_rule_based("xyzzy unknown gibberish foo bar")
    assert result["type"] == "general"
    assert result["style"] == "modern"
    assert result["platform"] == "mobile"


def test_parse_result_keys() -> None:
    result = parse_query_rule_based("login")
    assert set(result.keys()) == {"type", "style", "platform"}
