"""
Logging utilities for the MCP server.
"""

from __future__ import annotations

import logging
import os
import sys


def setup_logging() -> None:
    """
    Configure root logger based on LOG_LEVEL env var.
    Defaults to INFO. Logs go to stderr (MCP-compatible).
    """
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers when re-imported
    if not root.handlers:
        root.addHandler(handler)
    else:
        root.handlers = [handler]
