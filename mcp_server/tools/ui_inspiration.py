"""
MCP tool: get_ui_inspiration
Orchestrates parse → fetch → format → cache pipeline.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp_server.services.cache import cache
from mcp_server.services.formatter import format_response
from mcp_server.services.parser import parse_query
from mcp_server.services.scraper import fetch_ui_patterns

logger = logging.getLogger(__name__)


def _normalize_cache_key(query: str) -> str:
    """Lowercase + strip for consistent cache key regardless of user casing."""
    return " ".join(query.lower().split())


def get_ui_inspiration(query: str) -> dict[str, Any]:
    """
    Return structured UI/UX design inspiration for the given natural language query.

    Args:
        query: Free-form description of the desired UI, e.g.
               "modern fintech login screen" or "minimal todo app mobile UI".

    Returns:
        A dict with keys: query, type, style, platform, patterns, components,
        layout, design_notes, references, source, result_count.

    Raises:
        Never – all errors are caught and a graceful fallback is returned.
    """
    if not query or not query.strip():
        logger.warning("get_ui_inspiration called with empty query")
        query = "generic mobile ui"

    query = query.strip()
    cache_key = _normalize_cache_key(query)

    # 1. Cache check
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info("Returning cached result for query=%r", query)
        return cached  # type: ignore[return-value]

    try:
        # 2. Parse query → structured intent
        intent = parse_query(query)
        logger.info("Parsed intent: %s", intent)

        # 3. Fetch raw patterns
        patterns, source = fetch_ui_patterns(query, intent)

        # 4. Format into clean output
        result = format_response(query, intent, patterns, source)

    except Exception as exc:  # noqa: BLE001
        # Last-resort safety net – the tool must never surface a raw exception
        logger.error("Unhandled error in get_ui_inspiration: %s", exc, exc_info=True)
        result = {
            "query": query,
            "type": "general",
            "style": "modern",
            "platform": "mobile",
            "patterns": ["clean layout", "clear visual hierarchy"],
            "components": ["header", "body content", "primary CTA"],
            "layout": "scrollable content",
            "design_notes": "Focus on clarity, whitespace, and a single accent color.",
            "references": [],
            "source": "error_fallback",
            "result_count": 0,
        }

    # 5. Cache result
    cache.set(cache_key, result)
    logger.info("Stored result in cache for query=%r", query)

    return result
