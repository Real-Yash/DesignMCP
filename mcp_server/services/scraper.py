"""
Data fetch layer: uses the TinyFish REST API directly (raw SSE) to scrape
free, public UI inspiration sites. Routes queries to the best source based
on parsed intent. Falls back to the curated dataset on any failure.

Why raw httpx instead of the SDK?
  The TinyFish SDK's CompleteEvent model maps only the 'resultJson' alias, but
  the wire format sends the payload under the 'result' key. Pydantic silently
  drops unmapped keys, so result_json is always None through the SDK. Using
  httpx + manual SSE parsing avoids this.

Source routing:
  mobile / product UI  → Screenlane, UI Sources
  saas / web dashboard → Webframe, SaaSFrame
  landing page         → Lapa Ninja, Land-book
  creative / general   → SiteInspire, Godly
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import httpx

from mcp_server.data.fallback_data import FALLBACK_PATTERNS
from mcp_server.services.parser import ParsedIntent

logger = logging.getLogger(__name__)

_TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY", "")
_TINYFISH_URL = "https://agent.tinyfish.ai/v1/automation/run-sse"
_TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "120"))

# ---------------------------------------------------------------------------
# Source registry
# ---------------------------------------------------------------------------

_SOURCES: dict[str, list[dict[str, str]]] = {
    "mobile": [
        {
            "url": "https://screenlane.com/?s={query}",
            "goal": (
                'Search Screenlane for "{query}" UI screens. '
                "Extract the first 5 results visible on the page. For each return: "
                "screen_title (str), image_url (direct img src starting with https://), "
                "app_name (str), tags (list[str]). "
                "Return ONLY a valid JSON array. No markdown, no explanation."
            ),
        },
        {
            "url": "https://uisources.com/patterns/{type}",
            "goal": (
                'Find "{query}" UI patterns on this page. '
                "Extract the first 5 visible pattern cards. For each return: "
                "screen_title (str), image_url (direct img src starting with https://), "
                "description (str), tags (list[str]). "
                "Return ONLY a valid JSON array. No markdown, no explanation."
            ),
        },
    ],
    "saas": [
        {
            "url": "https://webframe.xyz/topic/{type}",
            "goal": (
                'Find "{query}" UI screens on this page. '
                "Extract the first 5 visible screenshots. For each return: "
                "screen_title (str), image_url (direct img src starting with https://), "
                "app_name (str), description (str). "
                "Return ONLY a valid JSON array. No markdown, no explanation."
            ),
        },
        {
            "url": "https://saasframe.io/categories/{type}",
            "goal": (
                'Find "{query}" UI patterns on this page. '
                "Extract the first 5 visible items. For each return: "
                "screen_title (str), image_url (direct img src starting with https://), "
                "app_name (str), tags (list[str]). "
                "Return ONLY a valid JSON array. No markdown, no explanation."
            ),
        },
    ],
    "landing": [
        {
            "url": "https://www.lapa.ninja",
            "goal": (
                'Find landing pages related to "{query}" on this page. '
                "Extract the first 5 visible landing page cards. For each return: "
                "screen_title (str), image_url (direct img src starting with https://), "
                "company_name (str), tags (list[str]). "
                "Return ONLY a valid JSON array. No markdown, no explanation."
            ),
        },
        {
            "url": "https://land-book.com",
            "goal": (
                'Find landing pages related to "{query}" on this page. '
                "Extract the first 5 visible items. For each return: "
                "screen_title (str), image_url (direct img src starting with https://), "
                "company_name (str). "
                "Return ONLY a valid JSON array. No markdown, no explanation."
            ),
        },
    ],
    "creative": [
        {
            "url": "https://www.siteinspire.com/websites?q={query}",
            "goal": (
                'Find website designs related to "{query}" on this page. '
                "Extract the first 5 visible website cards. For each return: "
                "screen_title (str), image_url (direct img src starting with https://), "
                "website_url (str), tags (list[str]). "
                "Return ONLY a valid JSON array. No markdown, no explanation."
            ),
        },
        {
            "url": "https://godly.website",
            "goal": (
                'Find creative website designs related to "{query}" on this page. '
                "Extract the first 5 visible site entries. For each return: "
                "screen_title (str), image_url (direct img src starting with https://), "
                "website_url (str). "
                "Return ONLY a valid JSON array. No markdown, no explanation."
            ),
        },
    ],
}

_TYPE_TO_BUCKET: dict[str, str] = {
    "login": "mobile", "signup": "mobile", "onboarding": "mobile",
    "home": "mobile", "profile": "mobile", "settings": "mobile",
    "todo": "mobile", "search": "mobile", "checkout": "mobile",
    "empty state": "mobile",
    "dashboard": "saas",
    "landing page": "landing",
    "general": "creative",
}
_SAAS_STYLES = {"saas", "b2b", "enterprise"}


def _pick_bucket(intent: ParsedIntent) -> str:
    style = intent["style"].lower()
    if intent["type"] == "landing page":
        return "landing"
    if style in _SAAS_STYLES or intent["platform"] == "web":
        return "saas"
    return _TYPE_TO_BUCKET.get(intent["type"], "mobile")


def _build_call(bucket: str, attempt: int, query: str, intent: ParsedIntent) -> tuple[str, str]:
    sources = _SOURCES[bucket]
    source = sources[attempt % len(sources)]
    slug_type = intent["type"].replace(" ", "-").lower()
    url = source["url"].format(query=query.replace(" ", "+"), type=slug_type)
    goal = source["goal"].format(query=query, type=slug_type)
    return url, goal


# ---------------------------------------------------------------------------
# Raw SSE fetch (bypasses SDK Pydantic mapping bug)
# ---------------------------------------------------------------------------

def _run_tinyfish_agent(target_url: str, goal: str) -> Any | None:
    """
    POST to TinyFish SSE endpoint, stream events, and return the result
    payload from the COMPLETE event. The wire key is 'result', not 'resultJson'.
    Returns None on failure.
    """
    headers = {
        "X-API-Key": _TINYFISH_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "url": target_url,
        "goal": goal,
        "browser_profile": "stealth",
    }

    try:
        with httpx.stream(
            "POST",
            _TINYFISH_URL,
            headers=headers,
            json=payload,
            timeout=_TIMEOUT,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if not data_str:
                    continue
                try:
                    event = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                ev_type = event.get("type", "")
                if ev_type == "PROGRESS":
                    logger.debug("TinyFish: %s", event.get("purpose", ""))
                elif ev_type == "COMPLETE":
                    status = event.get("status", "")
                    if status == "COMPLETED":
                        # Wire format: {"type":"COMPLETE","result":{"result":[...]} }
                        # or directly {"type":"COMPLETE","result":[...]}
                        raw_result = event.get("result")
                        logger.info("TinyFish COMPLETE — raw_result type: %s", type(raw_result).__name__)
                        return raw_result
                    else:
                        logger.warning("TinyFish COMPLETE status=%r", status)
                        return None
                elif ev_type == "FAILED":
                    logger.warning("TinyFish FAILED: %s", event.get("error", ""))
                    return None

    except httpx.HTTPStatusError as exc:
        logger.warning("TinyFish HTTP error: %s", exc)
    except Exception as exc:  # noqa: BLE001
        logger.error("TinyFish unexpected error: %s", exc, exc_info=True)

    return None


# ---------------------------------------------------------------------------
# Result normaliser
# ---------------------------------------------------------------------------

def _extract_list(raw: Any) -> list[dict]:
    """
    Coerce whatever the agent returned into a list of dicts.
    Handles: list, dict-with-single-list-value (double-wrap), JSON string.
    """
    if isinstance(raw, list):
        return [i for i in raw if isinstance(i, dict)]
    if isinstance(raw, dict):
        # double-wrap: {"result": [...]}
        for v in raw.values():
            if isinstance(v, list):
                return [i for i in v if isinstance(i, dict)]
        return [raw]
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return _extract_list(parsed)
        except json.JSONDecodeError:
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                try:
                    return _extract_list(json.loads(match.group()))
                except json.JSONDecodeError:
                    pass
    return []


def _extract_urls(item: dict) -> list[str]:
    urls: list[str] = []
    for key in ("image_url", "screenshot", "thumbnail", "url", "website_url"):
        val = item.get(key)
        if isinstance(val, str) and val.startswith("http"):
            urls.append(val)
    return urls


def _normalize(items: list[dict]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        tags = item.get("tags") or []
        normalized.append({
            "type": item.get("type") or "screen",
            "style": tags[0] if tags else "",
            "platform": "mobile",
            "layout": item.get("layout") or item.get("description") or "",
            "components": tags,
            "notes": item.get("description") or item.get("notes") or "",
            "references": _extract_urls(item),
            "_app": item.get("app_name") or item.get("company_name") or "",
            "_title": item.get("screen_title") or item.get("title") or "",
        })
    logger.info("Normalised %d patterns from live fetch", len(normalized))
    return normalized


# ---------------------------------------------------------------------------
# Primary fetch
# ---------------------------------------------------------------------------

def _fetch_from_tinyfish(query: str, intent: ParsedIntent) -> list[dict[str, Any]] | None:
    if not _TINYFISH_API_KEY:
        logger.debug("TINYFISH_API_KEY not set — skipping live fetch")
        return None

    bucket = _pick_bucket(intent)

    for attempt in range(2):
        target_url, goal = _build_call(bucket, attempt, query, intent)
        logger.info(
            "TinyFish attempt %d/2 → bucket=%r url=%r",
            attempt + 1, bucket, target_url,
        )

        raw = _run_tinyfish_agent(target_url, goal)
        if raw is None:
            logger.warning("Attempt %d: no result from agent", attempt + 1)
            continue

        items = _extract_list(raw)
        if not items:
            logger.warning("Attempt %d: agent returned data but 0 items extracted", attempt + 1)
            continue

        return _normalize(items)

    logger.warning("All TinyFish attempts exhausted for query=%r", query)
    return None


# ---------------------------------------------------------------------------
# Fallback selector
# ---------------------------------------------------------------------------

def _filter_fallback(intent: ParsedIntent) -> list[dict[str, Any]]:
    ui_type = intent["type"].lower()
    style = intent["style"].lower()
    platform = intent["platform"].lower()

    exact, partial, rest = [], [], []
    for p in FALLBACK_PATTERNS:
        p_type = p.get("type", "").lower()
        p_style = p.get("style", "").lower()
        p_platform = p.get("platform", "").lower()

        type_match = p_type == ui_type
        style_match = style in p_style or p_style in style
        platform_match = p_platform == platform

        if type_match and (style_match or platform_match):
            exact.append(p)
        elif type_match or style_match:
            partial.append(p)
        else:
            rest.append(p)

    ranked = (exact + partial + rest)[:5]
    logger.debug("Fallback: %d exact, %d partial → %d returned", len(exact), len(partial), len(ranked))
    return ranked


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_ui_patterns(query: str, intent: ParsedIntent) -> tuple[list[dict[str, Any]], str]:
    """
    Return ``(patterns, source)`` — source is ``"live"`` or ``"fallback"``.
    Never raises.
    """
    live = _fetch_from_tinyfish(query, intent)
    if live is not None:
        return live, "live"

    logger.info("Using fallback dataset for query=%r", query)
    return _filter_fallback(intent), "fallback"
