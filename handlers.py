"""
Kynari Bot - Message Handlers

Handles all Telegram bot commands and conversational messages,
coordinating between web search and Mistral AI.
"""

import logging
import re
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import MAX_SEARCH_RESULTS
from tools.web_search import search_web, format_search_results_for_prompt, WebSearchError
from tools.mistral_ai import generate_response, generate_greeting, MistralAIError

logger = logging.getLogger(__name__)

# Telegram message limit
TELEGRAM_MAX_LENGTH = 4096


# ─── Rate limiting ────────────────────────────────────────────────

_user_last_request: dict[int, float] = {}
RATE_LIMIT_SECONDS = 2.0


def _check_rate_limit(user_id: int) -> Optional[float]:
    """
    Check if the user is rate-limited.

    Args:
        user_id: Telegram user ID.

    Returns:
        Remaining wait time in seconds, or None if allowed.
    """
    import time

    now = time.time()
    last_time = _user_last_request.get(user_id, 0)
    elapsed = now - last_time

    if elapsed < RATE_LIMIT_SECONDS:
        return round(RATE_LIMIT_SECONDS - elapsed, 1)

    _user_last_request[user_id] = now
    return None


def _clean_response(text: str) -> str:
    """
    Clean and normalize AI response for Telegram HTML formatting.
    Removes all Markdown artifacts.
    """
    # Remove ### headers -> bold
    text = re.sub(r'^#{1,6}\s+(.+)$', r'<b>\1</b>', text, flags=re.MULTILINE)

    # Remove --- separators
    text = re.sub(r'-{3,}', '', text)

    # Remove ** bold -> HTML bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

    # Remove * italic -> HTML italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)

    # Remove ` code -> HTML code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)

    # Remove stray markdown bullets, keep clean ones
    text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)

    # Remove numbered list markdown (1. 2. etc) keep clean
    text = re.sub(r'^\s*\d+\.\s+', '• ', text, flags=re.MULTILINE)

    # Fix double-nested bold tags
    text = re.sub(r'<b><b>(.+?)</b></b>', r'<b>\1</b>', text)

    # Collapse multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def _truncate_for_telegram(text: str) -> str:
    """Truncate text to fit Telegram's message limit."""
    if len(text) <= TELEGRAM_MAX_LENGTH:
        return text
    return text[:TELEGRAM_MAX_LENGTH - 20] + "\n\n<i>... truncado</i>"


# ─── Helper: send typing indicator ───────────────────────────────

async def _send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a typing action to show the bot is working."""
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing",
    )


# ─── Command: /start ─────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    Sends a welcome message (AI-generated if possible).
    """
    user = update.effective_user
    logger.info(f"/start command from user {user.id} (@{user.username})")

    await _send_typing(update, context)

    try:
        greeting = await generate_greeting()
    except MistralAIError:
        greeting = (
            "Hola! Soy <b>Kynari</b>, tu asistente de busqueda inteligente.\n\n"
            "Puedes enviarme cualquier tema y buscare informacion actualizada en la web "
            "para darte un resumen claro y estructurado.\n\n"
            "<b>Comandos disponibles:</b>\n"
            "• /buscar &lt;tema&gt; — Busca informacion sobre un tema especifico\n"
            "• /help — Ver todos los comandos disponibles\n"
            "• O simplemente <b>escribe lo que quieras saber</b> y lo buscare por ti."
        )

    greeting = _clean_response(greeting)

    await update.message.reply_text(
        text=greeting,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# ─── Command: /help ──────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    Shows all available commands and usage instructions.
    """
    user = update.effective_user
    logger.info(f"/help command from user {user.id}")

    help_text = (
        "<b>Kynari Bot — Ayuda</b>\n\n"
        "Soy un asistente de busqueda inteligente. Puedo buscar informacion "
        "actualizada en la web y resumeirtela de forma clara.\n\n"
        "<b>Comandos disponibles:</b>\n\n"
        "• /start — Mensaje de bienvenida\n"
        "• /help — Esta ayuda\n"
        "• /buscar &lt;tema&gt; — Busca informacion sobre un tema\n\n"
        "<b>Modo conversacional:</b>\n"
        "Tambien puedes simplemente <b>escribir cualquier pregunta o tema</b> "
        "y lo buscara automaticamente por ti. Por ejemplo:\n"
        "• Que esta pasando en la economia global?\n"
        "• Hablame sobre inteligencia artificial\n"
        "• Ultimas noticias de tecnologia\n\n"
        "<i>Tip:</i> Se especifico para obtener mejores resultados.\n"
        "Ejemplo: en lugar de \"clima\", prueba \"clima en Buenos Aires esta semana\".\n\n"
        "<i>Limite de velocidad:</i> "
        "Puedes enviar 1 solicitud cada 2 segundos para evitar saturacion."
    )

    await update.message.reply_text(
        text=help_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# ─── Command: /buscar ────────────────────────────────────────────

async def buscar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /buscar <query> command.
    Performs a web search and returns an AI-summarized response.
    """
    user = update.effective_user

    # Extract search query from command arguments
    query = " ".join(context.args) if context.args else ""

    if not query:
        await update.message.reply_text(
            "<b>Uso correcto:</b> /buscar &lt;tema&gt;\n\n"
            "Ejemplo: /buscar inteligencia artificial 2025",
            parse_mode=ParseMode.HTML,
        )
        return

    logger.info(f"/buscar command from user {user.id}: '{query}'")
    await _perform_search_and_reply(update, context, query)


# ─── Message handler (conversational mode) ───────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle regular text messages as search queries (conversational mode).
    """
    user = update.effective_user
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if not text:
        return

    logger.info(f"Message from user {user.id}: '{text[:80]}...'")
    await _perform_search_and_reply(update, context, text)


# ─── Core search-and-reply logic ─────────────────────────────────

async def _perform_search_and_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    query: str,
) -> None:
    """
    Execute a web search, get an AI summary, and send the reply.
    Handles all errors and edge cases gracefully.
    """
    user_id = update.effective_user.id

    # Rate limit check
    wait_time = _check_rate_limit(user_id)
    if wait_time:
        await update.message.reply_text(
            f"<b>Demasiado rapido.</b> Espera {wait_time} segundos antes de enviar otra solicitud.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Send initial "searching" message
    searching_msg = await update.message.reply_text(
        "Buscando informacion...",
        parse_mode=ParseMode.HTML,
    )

    try:
        # Step 1: Search the web
        await _send_typing(update, context)
        results = await search_web(query)

        if not results:
            await searching_msg.edit_text(
                "<b>No encontre resultados</b> para tu busqueda.\n\n"
                "<b>Sugerencias:</b>\n"
                "• Prueba con palabras clave diferentes\n"
                "• Se mas especifico en tu consulta\n"
                "• Usa terminos en espanol o ingles",
                parse_mode=ParseMode.HTML,
            )
            return

        # Step 2: Format results for Mistral
        search_context = format_search_results_for_prompt(results)

        # Step 3: Update message to show we're generating the response
        await searching_msg.edit_text(
            "Analizando resultados...",
            parse_mode=ParseMode.HTML,
        )

        # Step 4: Generate AI response
        await _send_typing(update, context)
        response = await generate_response(query, search_context)

        # Step 5: Clean and send the final response
        logger.debug(f"Raw response ({len(response)} chars): {response[:200]}...")
        response = _clean_response(response)
        logger.debug(f"Cleaned response ({len(response)} chars): {response[:200]}...")
        response = _truncate_for_telegram(response)

        await searching_msg.edit_text(
            text=response,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    except WebSearchError as e:
        logger.error(f"Web search error: {e}")
        await searching_msg.edit_text(
            "<b>Error al buscar informacion.</b>\n\n"
            "Hubo un problema al realizar la busqueda web. "
            "Por favor, intenta de nuevo en unos momentos.\n\n"
            "Si el problema persiste, verifica tu conexion a internet.",
            parse_mode=ParseMode.HTML,
        )

    except MistralAIError as e:
        logger.error(f"Mistral AI error: {e}")
        await searching_msg.edit_text(
            "<b>Error al generar la respuesta.</b>\n\n"
            "Hubo un problema con el servicio de inteligencia artificial. "
            "Por favor, intenta de nuevo en unos momentos.",
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:
        logger.exception(f"Unexpected error processing query '{query}': {e}")
        await searching_msg.edit_text(
            "<b>Ocurrio un error inesperado.</b>\n\n"
            "Algo salio mal al procesar tu solicitud. "
            "Por favor, intenta de nuevo mas tarde.",
            parse_mode=ParseMode.HTML,
        )


# ─── Error handler ───────────────────────────────────────────────

async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors that occur during bot operation.
    Logs the error and notifies the user if possible.
    """
    logger.error(f"Exception while handling an update: {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "<b>Error interno.</b>\n\n"
            "Ocurrio un error mientras procesaba tu solicitud. "
            "Por favor, intenta de nuevo mas tarde.",
            parse_mode=ParseMode.HTML,
        )
