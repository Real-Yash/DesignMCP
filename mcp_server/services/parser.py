"""
Query parser: converts a free-form natural language query into a structured
intent dict with 'type', 'style', and 'platform' keys.

Primary implementation: fast rule-based keyword matching.
Optional: LLM-based enhancement when OPENROUTER_API_KEY is configured.
"""

from __future__ import annotations

import logging
import os
import re
from typing import TypedDict

logger = logging.getLogger(__name__)


class ParsedIntent(TypedDict):
    type: str
    style: str
    platform: str


# ---------------------------------------------------------------------------
# Keyword lookup tables
# ---------------------------------------------------------------------------

_TYPE_KEYWORDS: dict[str, list[str]] = {
    "login": ["login", "sign in", "signin", "sign-in", "auth", "authentication"],
    "signup": ["sign up", "signup", "register", "registration", "create account", "onboard"],
    "onboarding": ["onboarding", "welcome", "walkthrough", "getting started", "intro"],
    "dashboard": ["dashboard", "analytics", "metrics", "statistics", "stats", "overview", "admin"],
    "home": ["home", "homepage", "feed", "news feed", "main screen"],
    "profile": ["profile", "account", "user page", "bio", "portfolio"],
    "settings": ["settings", "preferences", "configuration", "config"],
    "checkout": ["checkout", "payment", "buy", "purchase", "cart", "order"],
    "todo": ["todo", "to-do", "task", "tasks", "list", "checklist", "planner"],
    "search": ["search", "explore", "discovery", "browse"],
    "landing page": ["landing", "landing page", "marketing page", "hero"],
    "empty state": ["empty state", "empty", "no results", "placeholder"],
}

_STYLE_KEYWORDS: dict[str, list[str]] = {
    "fintech": ["fintech", "finance", "banking", "bank", "payment", "wallet", "money", "crypto", "trading"],
    "saas": ["saas", "b2b", "enterprise", "productivity"],
    "ecommerce": ["ecommerce", "e-commerce", "shop", "shopping", "retail", "store"],
    "social": ["social", "community", "network", "chat", "messaging"],
    "health": ["health", "fitness", "wellness", "medical", "healthcare", "gym"],
    "travel": ["travel", "booking", "hotel", "flight", "airbnb", "trip"],
    "minimal": ["minimal", "minimalist", "clean", "simple", "flat"],
    "dark mode": ["dark", "dark mode", "night mode"],
    "glassmorphism": ["glass", "glassmorphism", "frosted"],
    "material": ["material", "material design", "android"],
    "ios native": ["ios", "apple", "native ios", "cupertino"],
    "consumer app": ["consumer", "mobile app", "app"],
}

_PLATFORM_KEYWORDS: dict[str, list[str]] = {
    "mobile": ["mobile", "ios", "android", "phone", "smartphone", "app"],
    "web": ["web", "desktop", "browser", "website", "saas", "dashboard"],
    "tablet": ["tablet", "ipad"],
}


def _match_keywords(text: str, table: dict[str, list[str]]) -> str:
    """Return the first key whose keywords appear in *text*, or empty string."""
    lower = text.lower()
    for label, keywords in table.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", lower):
                return label
    return ""


def parse_query_rule_based(query: str) -> ParsedIntent:
    """
    Fast, deterministic query parser using keyword matching.

    Returns a ``ParsedIntent`` with best-guess values; falls back to
    generic defaults when keywords are not found.
    """
    ui_type = _match_keywords(query, _TYPE_KEYWORDS) or "general"
    style = _match_keywords(query, _STYLE_KEYWORDS) or "modern"
    platform = _match_keywords(query, _PLATFORM_KEYWORDS) or "mobile"

    intent: ParsedIntent = {"type": ui_type, "style": style, "platform": platform}
    logger.debug("Rule-based parse of %r → %s", query, intent)
    return intent


# ---------------------------------------------------------------------------
# Optional LLM-based parser (OpenRouter)
# ---------------------------------------------------------------------------

def parse_query_llm(query: str) -> ParsedIntent | None:
    """
    Parse query with an LLM via OpenRouter. Returns ``None`` on failure so the
    caller can fall back to rule-based parsing.

    Requires env vars:
        OPENROUTER_API_KEY  – your OpenRouter key
        OPENROUTER_MODEL    – model slug (default: mistralai/mistral-7b-instruct)
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    try:
        import json

        import requests  # type: ignore[import-untyped]

        model = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")
        system_prompt = (
            "You are a UI/UX classification system. "
            "Given a natural language query, respond ONLY with valid JSON "
            "containing exactly three keys: "
            '"type" (e.g. login, dashboard, onboarding, profile, settings, checkout, todo, search, home, landing page), '
            '"style" (e.g. fintech, saas, minimal, ecommerce, social, health, travel, dark mode, ios native), '
            '"platform" (mobile | web | tablet). '
            "No explanation, no markdown fences, just raw JSON."
        )
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            "max_tokens": 80,
            "temperature": 0.2,
        }
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        parsed = json.loads(raw)
        intent: ParsedIntent = {
            "type": str(parsed.get("type", "general")),
            "style": str(parsed.get("style", "modern")),
            "platform": str(parsed.get("platform", "mobile")),
        }
        logger.debug("LLM parse of %r → %s", query, intent)
        return intent
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM parser failed (%s), falling back to rule-based", exc)
        return None


def parse_query(query: str) -> ParsedIntent:
    """
    Public entry point. Tries LLM parser first (if configured), then falls
    back to rule-based parsing.
    """
    llm_result = parse_query_llm(query)
    if llm_result is not None:
        return llm_result
    return parse_query_rule_based(query)
