"""
Kynari Bot - Web Search Tool

Provides web search functionality using DuckDuckGo.
No API key required.
"""

import asyncio
import logging
from typing import Optional

from ddgs import DDGS

from config import MAX_SEARCH_RESULTS, SEARCH_TIMELIMIT

logger = logging.getLogger(__name__)


class WebSearchError(Exception):
    """Custom exception for web search failures."""
    pass


async def search_web(
    query: str,
    max_results: Optional[int] = None,
    **kwargs,
) -> list[dict]:
    """
    Search the web using DuckDuckGo and return structured results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (defaults to config value).

    Returns:
        A list of dictionaries with 'title', 'url', and 'snippet' keys.

    Raises:
        WebSearchError: If the search fails for any reason.
    """
    if max_results is None:
        max_results = MAX_SEARCH_RESULTS

    if not query or not query.strip():
        raise WebSearchError("Empty search query provided.")

    try:
        logger.info(f"Searching web via DuckDuckGo: '{query}' (max_results={max_results}, timelimit={SEARCH_TIMELIMIT})")

        def _sync_search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results, timelimit=SEARCH_TIMELIMIT))

        raw_results = await asyncio.to_thread(_sync_search)

        if not raw_results:
            logger.warning(f"No results found for query: '{query}'")
            return []

        results = []
        for item in raw_results:
            result = {
                "title": item.get("title", "").strip(),
                "url": item.get("href", ""),
                "snippet": item.get("body", "").strip(),
            }
            if result["title"] and result["snippet"]:
                results.append(result)

        logger.info(f"Found {len(results)} results for query: '{query}'")
        return results

    except WebSearchError:
        raise
    except Exception as e:
        error_msg = f"Web search failed for query '{query}': {str(e)}"
        logger.error(error_msg)
        raise WebSearchError(error_msg) from e


def format_search_results_for_prompt(results: list[dict]) -> str:
    """
    Format search results into a clean text block for the AI prompt.

    Args:
        results: List of search result dictionaries.

    Returns:
        A formatted string with numbered results including title, snippet, and URL.
    """
    if not results:
        return "No se encontraron resultados relevantes en la web."

    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(
            f"[{i}] {result['title']}\n"
            f"    Resumen: {result['snippet']}\n"
            f"    Fuente: {result['url']}\n"
        )

    return "\n".join(formatted)
