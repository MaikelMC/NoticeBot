# AGENTS.md

## Project Overview

**Kynari Bot** — a Telegram bot that searches the web and returns AI-summarized responses in Spanish. Uses **Tavily** for web search and **Mistral AI** for summarization.

## Quick Start

```bash
# 1. Activate venv (Windows)
venv\Scripts\activate

# 2. Install deps
pip install -r requirements.txt

# 3. Copy env and fill in secrets
copy .env.example .env

# 4. Run (polling mode)
python bot.py
```

## Required Environment Variables

| Variable | Purpose | Source |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot auth | @BotFather |
| `MISTRAL_API_KEY` | AI summarization | console.mistral.ai |
| `TAVILY_API_KEY` | Web search | tavily.com |
| `USE_WEBHOOK` | `true` for Render prod, `false` for local dev | |
| `WEBHOOK_URL` | Set in Render: `https://yourapp.onrender.com` | |

## Architecture

- **`bot.py`** — Entry point. Registers handlers, runs polling or webhook mode.
- **`config.py`** — Loads `.env` via `python-dotenv`. Exports all config + logger.
- **`handlers.py`** — Telegram command/message handlers. Rate limits (2s/user). Core flow: search → format → Mistral → reply.
- **`tools/web_search.py`** — Tavily API wrapper (async). Singleton client. Max 8 results by default.
- **`tools/mistral_ai.py`** — Mistral chat API (async). System prompt forces Spanish responses. Model: `mistral-large-latest`.

## Deployment

- **Render**: `Procfile` + `runtime.txt` (Python 3.11) already included.
- Webhook mode: bot listens on `PORT` env var (default 8443), path is the bot token itself.
- Polling mode: just `python bot.py` locally.

## Conventions

- All user-facing text is in **Spanish**.
- Responses use **Markdown** (not HTML).
- Custom exceptions: `WebSearchError`, `MistralAIError` — catch these specifically in handlers.
- Logging goes to stdout via `config.logger`.

## Gotchas

- **README says DuckDuckGo** but the code actually uses **Tavily** (`tools/web_search.py`). If you search for DuckDuckGo references, they're stale — the real search backend is Tavily.
- `python-telegram-bot` >=22 uses **async-only** API. All handler functions are `async`.
- Mistral client is instantiated per-call (`get_client()` in `tools/mistral_ai.py`), not a singleton like Tavily.
- No test suite exists. No linter or formatter is configured.
