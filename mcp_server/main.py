"""
MCP Server entry point.

Start with:
    python -m mcp_server.main          # stdio transport (default for MCP clients)

Or via the installed script:
    ui-inspiration-mcp
"""

from __future__ import annotations

from mcp_server.utils.logging import setup_logging

setup_logging()  # Must be called before any other imports that log.

import logging  # noqa: E402

from mcp import tool as mcp_tool  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402

from mcp_server.tools.ui_inspiration import get_ui_inspiration as _get_ui_inspiration  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Server initialisation
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="ui-inspiration",
    version="1.0.0",
    description=(
        "Provides structured UI/UX design inspiration to AI coding agents. "
        "Powered by Mobbin via TinyFish API with intelligent fallback patterns."
    ),
)

# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


@mcp.tool()
def get_ui_inspiration(query: str) -> dict:
    """
    Get structured UI/UX design inspiration for a given natural language query.

    Accepts a free-form description such as:
    - "modern fintech login screen"
    - "minimal todo app mobile UI"
    - "saas analytics dashboard dark mode"

    Returns a structured dict containing UI type, style, layout, component list,
    design notes, and reference URLs — all optimised for AI code generation context.

    Args:
        query: Natural language description of the desired UI screen or pattern.

    Returns:
        dict with keys: query, type, style, platform, patterns, components,
        layout, design_notes, references, source, result_count.
    """
    logger.info("Tool invoked: get_ui_inspiration(query=%r)", query)
    return _get_ui_inspiration(query)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("Starting UI Inspiration MCP server (stdio transport)")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
