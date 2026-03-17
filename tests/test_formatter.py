"""Tests for the formatter service."""

from __future__ import annotations

from mcp_server.services.formatter import format_response
from mcp_server.services.parser import ParsedIntent


def _intent(ui_type: str = "login", style: str = "fintech", platform: str = "mobile") -> ParsedIntent:
    return ParsedIntent(type=ui_type, style=style, platform=platform)


def test_format_response_schema() -> None:
    patterns = [
        {
            "type": "login",
            "style": "fintech",
            "platform": "mobile",
            "layout": "centered card",
            "components": ["email input", "password input"],
            "notes": "Trust-focused blue tones.",
            "references": ["https://mobbin.com/screen1"],
        }
    ]
    result = format_response("fintech login", _intent(), patterns, "fallback")
    required_keys = {
        "query", "type", "style", "platform", "patterns",
        "components", "layout", "design_notes", "references",
        "source", "result_count",
    }
    assert required_keys == set(result.keys())


def test_format_response_deduplicates_components() -> None:
    patterns = [
        {"components": ["email input", "password input"], "layout": "card", "notes": "", "references": []},
        {"components": ["email input", "submit button"], "layout": "", "notes": "", "references": []},
    ]
    result = format_response("test", _intent(), patterns)
    # "email input" should appear exactly once
    assert result["components"].count("email input") == 1


def test_format_response_empty_patterns() -> None:
    """Must not crash on empty pattern list."""
    result = format_response("empty query", _intent("general", "modern", "mobile"), [])
    assert result["result_count"] == 0
    assert isinstance(result["patterns"], list)
    assert isinstance(result["design_notes"], str)


def test_layout_fallback_per_type() -> None:
    for ui_type, expected_layout in [
        ("login", "centered card"),
        ("dashboard", "sidebar + main content"),
        ("todo", "flat list"),
    ]:
        result = format_response("q", _intent(ui_type=ui_type), [])
        assert result["layout"] == expected_layout, f"wrong layout for type={ui_type!r}"


def test_source_field_preserved() -> None:
    result = format_response("q", _intent(), [], source="live")
    assert result["source"] == "live"
