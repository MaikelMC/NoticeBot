"""
Kynari Bot - Main Entry Point

A Telegram bot that searches the web and provides AI-summarized responses.
Supports both polling (development) and webhook (production on Render) modes.
"""

import logging
import sys

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    USE_WEBHOOK,
    WEBHOOK_URL,
    WEBHOOK_PORT,
    WEBHOOK_LISTEN,
    logger,
)
from handlers import (
    start_command,
    help_command,
    buscar_command,
    handle_message,
    error_handler,
)

# Suppress httpx verbose logging
logging.getLogger("httpx").setLevel(logging.WARNING)


def build_application() -> Application:
    """
    Build and configure the Telegram bot application.

    Returns:
        A configured Application instance with all handlers registered.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN is not set. Cannot start bot.")
        sys.exit(1)

    logger.info("Building Kynari Bot application...")

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .concurrent_updates(True)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # ─── Register command handlers ───────────────────────────────
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("buscar", buscar_command))

    # ─── Register message handler (conversational mode) ──────────
    # Handles all text messages that are not commands
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # ─── Register error handler ──────────────────────────────────
    application.add_error_handler(error_handler)

    logger.info("Bot application built successfully.")
    return application


def run_polling(application: Application) -> None:
    """
    Run the bot in polling mode (development).

    Args:
        application: The configured Application instance.
    """
    logger.info("Starting bot in POLLING mode (development)...")
    print(">> Kynari Bot iniciado en modo POLLING.")
    print("Presiona Ctrl+C para detener el bot.")
    print("-" * 50)

    application.run_polling(allowed_updates=["message", "callback_query"])


def run_webhook(application: Application) -> None:
    """
    Run the bot in webhook mode (production).

    Args:
        application: The configured Application instance.
    """
    if not WEBHOOK_URL:
        logger.warning("WEBHOOK_URL is not set. Falling back to polling mode.")
        run_polling(application)
        return

    logger.info(f"Starting bot in WEBHOOK mode on port {WEBHOOK_PORT}...")
    print(f">> Kynari Bot iniciado en modo WEBHOOK.")
    print(f"   URL: {WEBHOOK_URL}")
    print(f"   Puerto: {WEBHOOK_PORT}")
    print("-" * 50)

    application.run_webhook(
        listen=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}",
    )


def main() -> None:
    """Main entry point."""
    logger.info("=" * 50)
    logger.info("Kynari Bot starting...")
    logger.info("=" * 50)

    application = build_application()

    if USE_WEBHOOK:
        run_webhook(application)
    else:
        run_polling(application)


if __name__ == "__main__":
    main()
