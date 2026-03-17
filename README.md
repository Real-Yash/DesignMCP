# UI Inspiration MCP Server

A production-ready **Model Context Protocol (MCP) server** that provides structured UI/UX design inspiration to AI coding agents — powered by Mobbin via the TinyFish API with an intelligent fallback dataset.

---

## Features

| Feature | Detail |
|---|---|
| **MCP Tool** | `get_ui_inspiration(query)` |
| **Query Parsing** | Rule-based (always on) + optional LLM via OpenRouter |
| **Data Source** | TinyFish/Mobbin API (live) or curated fallback dataset |
| **Caching** | In-memory TTL cache (1 hour, thread-safe) |
| **Transport** | stdio (MCP standard) |

---

## Project Structure

```
mcp_server/
├── main.py                 # FastMCP server + tool registration
├── tools/
│   └── ui_inspiration.py   # Tool orchestration (parse → fetch → format → cache)
├── services/
│   ├── parser.py           # Query → structured intent
│   ├── scraper.py          # TinyFish API + fallback selection
│   ├── formatter.py        # Raw patterns → clean output schema
│   └── cache.py            # In-memory TTL cache
├── data/
│   └── fallback_data.py    # 12 curated UI patterns
└── utils/
    └── logging.py          # Structured logging setup
test_tool.py                # CLI validation script
```

---

## Quick Start

### 1. Install

```bash
pip install -e ".[dev]"
```

### 2. Run the CLI test script

```bash
# Single query
python test_tool.py "modern fintech login screen"

# Full built-in suite (8 queries)
python test_tool.py --all
```

### 3. Start the MCP server

```bash
# As a Python module
python -m mcp_server.main

# Via installed script
ui-inspiration-mcp
```

---

## Connect to Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ui-inspiration": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/path/to/mcp"
    }
  }
}
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TINYFISH_API_KEY` | _(empty)_ | TinyFish API key for live Mobbin data |
| `TINYFISH_API_URL` | TinyFish endpoint | Override base URL |
| `SCRAPER_TIMEOUT` | `8` | HTTP timeout in seconds |
| `OPENROUTER_API_KEY` | _(empty)_ | Enables LLM-based query parsing |
| `OPENROUTER_MODEL` | `mistralai/mistral-7b-instruct` | Model for LLM parsing |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

---

## Tool Output Schema

```json
{
  "query": "fintech login mobile",
  "type": "login",
  "style": "fintech",
  "platform": "mobile",
  "patterns": ["centered card"],
  "components": ["email input", "password input", "login button", "social login"],
  "layout": "centered card",
  "design_notes": "Minimal trust-focused design. Blue/navy tones, rounded corners, subtle drop shadows.",
  "references": ["https://mobbin.com/screens/revolut-login"],
  "source": "fallback",
  "result_count": 3
}
```

---

## Running Tests

```bash
pytest
```
