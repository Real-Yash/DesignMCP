"""
Response formatter: transforms raw pattern data into the clean, structured
output schema expected by the MCP tool consumer.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp_server.services.parser import ParsedIntent

logger = logging.getLogger(__name__)


def _deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


def _collect_field(patterns: list[dict[str, Any]], field: str) -> list[str]:
    """Collect and deduplicate a list-valued field across all patterns."""
    items: list[str] = []
    for p in patterns:
        val = p.get(field, [])
        if isinstance(val, list):
            items.extend(str(v) for v in val if v)
        elif isinstance(val, str) and val:
            items.append(val)
    return _deduplicate(items)


def _infer_layout(patterns: list[dict[str, Any]], intent: ParsedIntent) -> str:
    """Best-guess layout from pattern data or intent type."""
    for p in patterns:
        layout = p.get("layout", "")
        if layout:
            return layout

    # Generic layout defaults per UI type
    defaults: dict[str, str] = {
        "login": "centered card",
        "signup": "centered form",
        "onboarding": "paginated full-screen",
        "dashboard": "sidebar + main content",
        "home": "scrollable feed",
        "profile": "header + scrollable content",
        "settings": "grouped list",
        "checkout": "stepper form",
        "todo": "flat list",
        "search": "search bar + results list",
        "landing page": "hero + sections + footer",
        "empty state": "centered illustration",
    }
    return defaults.get(intent["type"], "scrollable content")


def _generate_design_notes(patterns: list[dict[str, Any]], intent: ParsedIntent) -> str:
    """
    Synthesise concise design notes from pattern notes and the intent style.
    """
    raw_notes: list[str] = []
    for p in patterns:
        note = p.get("notes", "")
        if isinstance(note, str) and note.strip():
            raw_notes.append(note.strip())

    if raw_notes:
        # Use the first (most relevant) note as the primary guidance
        primary = raw_notes[0]
        # Append extras if they add unique info (crude similarity gate)
        extras = [n for n in raw_notes[1:] if n[:40] != primary[:40]]
        combined = primary
        if extras:
            combined += " | " + " | ".join(extras[:2])
        return combined

    # Generated fallback based on style / type
    style_hints: dict[str, str] = {
        "fintech": "Use blue/navy palette with high-contrast CTAs. Communicate trust and security.",
        "saas": "Clean whitespace, neutral grays, one bold accent color. Data-forward layout.",
        "minimal": "Single accent color, generous whitespace, lightweight typography.",
        "ecommerce": "Product imagery dominant. Price prominence. Clear purchase CTA.",
        "social": "User-generated content at center. Strong avatar/identity signals.",
        "health": "Calming greens or soft purples. Progress indicators and streaks.",
        "travel": "Rich photography full-bleed. Price transparency up front.",
        "dark mode": "Dark gray surfaces (#1E1E2E), vibrant accent (electric blue/purple).",
        "ios native": "SF Pro typography, grouped table view, iOS-standard navigation bar.",
    }
    return style_hints.get(intent["style"], "Follow platform-native conventions with clean visual hierarchy.")


def format_response(
    query: str,
    intent: ParsedIntent,
    patterns: list[dict[str, Any]],
    source: str = "fallback",
) -> dict[str, Any]:
    """
    Build the final agent-ready response dict.

    Schema:
        query        – original user query
        type         – parsed UI type
        style        – parsed style
        platform     – parsed platform
        patterns     – list of high-level pattern labels
        components   – deduplicated component list
        layout       – inferred or extracted layout string
        design_notes – concise design guidance
        references   – image/URL references
        source       – "live" | "fallback"
        result_count – number of patterns found
    """
    if not patterns:
        logger.warning("format_response called with empty patterns list")
        patterns = []

    # High-level pattern labels
    pattern_labels = _deduplicate(
        [p.get("layout", "") or p.get("type", "") for p in patterns if p.get("layout") or p.get("type")]
    )

    components = _collect_field(patterns, "components")
    references = _collect_field(patterns, "references")
    layout = _infer_layout(patterns, intent)
    design_notes = _generate_design_notes(patterns, intent)

    response: dict[str, Any] = {
        "query": query,
        "type": intent["type"],
        "style": intent["style"],
        "platform": intent["platform"],
        "patterns": pattern_labels or [f"{intent['style']} {intent['type']}"],
        "components": components,
        "layout": layout,
        "design_notes": design_notes,
        "references": references,
        "source": source,
        "result_count": len(patterns),
    }

    logger.debug("Formatted response for query=%r: %d components, %d refs", query, len(components), len(references))
    return response
