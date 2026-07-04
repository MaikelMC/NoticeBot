"""
Kynari Bot - Mistral AI Integration

Handles communication with Mistral AI API for generating
summarized, structured responses from web search results.
"""

import logging
from mistralai import Mistral

from config import MISTRAL_API_KEY, MISTRAL_MODEL

logger = logging.getLogger(__name__)


class MistralAIError(Exception):
    """Custom exception for Mistral AI failures."""
    pass


# System prompt optimized for information search and summarization in Spanish
SYSTEM_PROMPT = """
Eres Kynari, un asistente de busqueda de informacion profesional, preciso y util.
Tu mision es ayudar al usuario a encontrar y comprender informacion actualizada.

## REGLAS CRITICAS DE FORMATO:
NO uses NUNCA estos caracteres o patronas:
- NO uses # ni ## ni ### (cero headers markdown)
- NO uses ** ni * (cero asteriscos)
- NO uses --- ni ___ (cero separadores)
- NO uses ``` ni ` (cero backticks)
- NO uses [] ni () (cero links markdown)

USA SOLO estas etiquetas HTML:
- <b>texto</b> para negritas
- <i>texto</i> para cursivas
- <a href="url">texto</a> para enlaces

## Reglas importantes:
1. Responde SIEMPRE en espanol, sin importar el idioma de la consulta.
2. Proporciona respuestas claras, estructuradas y faciles de leer.
3. Si la informacion de busqueda es suficiente, entrega un resumen util.
4. Si la informacion es insuficiente, indicalo honestamente.
5. NO inventes datos ni fuentes. Solo usa la informacion proporcionada.

## Estructura de respuesta (usa HTML, NO Markdown):
<b>Resumen:</b> 1-2 oraciones con la respuesta principal.

<b>Puntos clave:</b>
• Primer punto importante
• Segundo punto importante
• Tercer punto importante

<b>Fuentes:</b>
Enlaces a las fuentes consultadas cuando esten disponibles.

Manten un tono profesional pero amigable. Se conciso pero completo.
"""


def _build_search_prompt(user_query: str, search_context: str) -> str:
    """
    Build the full prompt for Mistral including search context.

    Args:
        user_query: The original user query.
        search_context: Formatted search results.

    Returns:
        A complete prompt string for Mistral.
    """
    return f"""
## Consulta del usuario:
{user_query}

## Resultados de búsqueda web:
{search_context}

---

Con base en la información de búsqueda proporcionada arriba, responde a la consulta del usuario de manera clara, estructurada y útil. Si los resultados no contienen suficiente información para responder adecuadamente, indícalo y sugiere cómo refinar la búsqueda.
"""


def get_client() -> Mistral:
    """
    Initialize and return a Mistral AI client.

    Returns:
        A configured Mistral client instance.

    Raises:
        MistralAIError: If the API key is missing.
    """
    if not MISTRAL_API_KEY:
        raise MistralAIError("Mistral API key is not configured. Set MISTRAL_API_KEY in .env")

    return Mistral(api_key=MISTRAL_API_KEY)


async def generate_response(
    user_query: str,
    search_context: str,
    model: str | None = None,
) -> str:
    """
    Generate a response using Mistral AI based on search results.

    Args:
        user_query: The original user query.
        search_context: Formatted search results text.
        model: Mistral model to use (defaults to config value).

    Returns:
        The generated response text.

    Raises:
        MistralAIError: If the API call fails.
    """
    if model is None:
        model = MISTRAL_MODEL

    client = get_client()
    prompt = _build_search_prompt(user_query, search_context)

    try:
        logger.info(
            f"Sending request to Mistral AI (model={model}, "
            f"query_len={len(user_query)}, context_len={len(search_context)})"
        )

        response = await client.chat.complete_async(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        if not response or not response.choices:
            raise MistralAIError("Empty response from Mistral AI")

        reply = response.choices[0].message.content.strip()
        logger.info(f"Response generated successfully ({len(reply)} chars)")
        return reply

    except Exception as e:
        error_msg = f"Mistral AI request failed: {str(e)}"
        logger.error(error_msg)
        raise MistralAIError(error_msg) from e


async def generate_greeting() -> str:
    """
    Generate a dynamic welcome message using Mistral.

    Returns:
        A welcome message string.
    """
    client = get_client()

    try:
        response = await client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres Kynari, un asistente de busqueda de informacion. "
                        "Genera un mensaje de bienvenida corto, profesional y amigable "
                        "en espanol. Incluye una breve descripcion de lo que puedes hacer "
                        "buscar informacion en la web y resumirla. "
                        "Usa SOLO formato HTML simple: <b>negritas</b> y <i>cursivas</i>. "
                        "NO uses Markdown ni ## ni **."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Dame un mensaje de bienvenida para un nuevo usuario. "
                        "Maximo 4 lineas. Se directo y util."
                    ),
                },
            ],
            temperature=0.7,
            max_tokens=300,
        )

        if response and response.choices:
            return response.choices[0].message.content.strip()

    except Exception as e:
        logger.warning(f"Could not generate greeting, using fallback: {e}")

    # Fallback greeting
    return (
        "Hola! Soy <b>Kynari</b>, tu asistente de busqueda inteligente.\n\n"
        "Puedes enviarme cualquier tema y buscare informacion actualizada en la web "
        "para darte un resumen claro y estructurado.\n\n"
        "<b>Comandos disponibles:</b>\n"
        "• /buscar &lt;tema&gt; — Busca informacion sobre un tema especifico\n"
        "• /help — Ver todos los comandos disponibles\n"
        "• O simplemente <b>escribe lo que quieras saber</b> y lo buscare por ti."
    )
