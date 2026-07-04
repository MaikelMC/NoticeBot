"""
Kynari Bot - Configuration Module

Loads environment variables and provides configuration
for the Telegram bot, Mistral AI, and web search.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Telegram Bot ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    logging.warning("TELEGRAM_BOT_TOKEN is not set!")

# --- Mistral AI ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
if not MISTRAL_API_KEY:
    logging.warning("MISTRAL_API_KEY is not set!")

# --- Web Search (Tavily) ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
if not TAVILY_API_KEY:
    logging.warning("TAVILY_API_KEY is not set!")
TAVILY_SEARCH_DEPTH = os.getenv("TAVILY_SEARCH_DEPTH", "advanced")
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "8"))

# --- Bot Settings ---
BOT_USERNAME = os.getenv("BOT_USERNAME", "KynariBot")
BOT_LANGUAGE = os.getenv("BOT_LANGUAGE", "es")

# --- Webhook (optional, for production on Render) ---
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.getenv("PORT", "8443"))
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)

logger = logging.getLogger(__name__)
