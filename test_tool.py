#!/usr/bin/env python3
"""
CLI test script for the UI Inspiration MCP tool.

Usage:
    python test_tool.py
    python test_tool.py "dark saas dashboard mobile"
    python test_tool.py --all        # run the full built-in test suite
"""

from __future__ import annotations

import json
import sys

# Ensure local package is importable when running from the project root.
try:
    from mcp_server.tools.ui_inspiration import get_ui_inspiration
    from mcp_server.utils.logging import setup_logging
except ModuleNotFoundError:
    print("[ERROR] Run this script from the project root: python test_tool.py")
    sys.exit(1)

setup_logging()

BUILT_IN_QUERIES = [
    "fintech login mobile",
    "minimal todo app mobile UI",
    "saas analytics dashboard dark mode",
    "ecommerce checkout web",
    "social profile screen ios",
    "travel search results mobile",
    "health onboarding mobile",
    "landing page saas startup web",
]


def run_query(query: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  Query: {query!r}")
    print("─" * 60)
    result = get_ui_inspiration(query)
    print(json.dumps(result, indent=2))


def main() -> None:
    args = sys.argv[1:]

    if "--all" in args:
        print(f"Running {len(BUILT_IN_QUERIES)} built-in test queries …\n")
        for q in BUILT_IN_QUERIES:
            run_query(q)
    elif args:
        run_query(" ".join(args))
    else:
        # Default demo query
        run_query("modern fintech login screen")

    print(f"\n{'─' * 60}")
    print("Done.")


if __name__ == "__main__":
    main()
