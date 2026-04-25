"""Web search tools.

Provides ``tavily_search`` and ``fetch_webpage_content`` for the research agent.
Despite the legacy tool name, the default search backend is DDGS (DuckDuckGo),
with Tavily used only as an optional fallback when configured.
"""

import asyncio
import os
from typing import Annotated, Literal

import httpx
from langchain_core.tools import InjectedToolArg, tool
from markdownify import markdownify

# Lazy initialization - only create clients when needed
_tavily_client = None


def _get_tavily_client():
    """Get or create the Tavily client (lazy initialization)."""
    global _tavily_client
    if _tavily_client is None:
        from tavily import TavilyClient

        _tavily_client = TavilyClient()
    return _tavily_client


def _ddgs_search(query: str, max_results: int) -> list[dict[str, str]]:
    """Search with DDGS and normalize results."""
    try:
        from ddgs import DDGS
    except ImportError as exc:
        raise RuntimeError(
            "DDGS is not installed. Install the `ddgs` package to enable default web search."
        ) from exc

    with DDGS() as client:
        raw_results = list(client.text(query, max_results=max_results))

    normalized: list[dict[str, str]] = []
    for item in raw_results:
        url = item.get("href") or item.get("url") or ""
        if not url:
            continue
        normalized.append(
            {
                "title": item.get("title") or url,
                "url": url,
                "snippet": item.get("body") or item.get("snippet") or "",
            }
        )
    return normalized


def _tavily_search_results(
    query: str, max_results: int, topic: Literal["general", "news", "finance"]
) -> list[dict[str, str]]:
    """Search with Tavily and normalize results."""
    raw_results = _get_tavily_client().search(
        query,
        max_results=max_results,
        topic=topic,
    )
    normalized: list[dict[str, str]] = []
    for item in raw_results.get("results", []):
        url = item.get("url", "")
        if not url:
            continue
        normalized.append(
            {
                "title": item.get("title") or url,
                "url": url,
                "snippet": item.get("content") or item.get("snippet") or "",
            }
        )
    return normalized


def _search_with_fallback(
    query: str,
    max_results: int,
    topic: Literal["general", "news", "finance"],
) -> tuple[str, list[dict[str, str]], list[str]]:
    """Search with DDGS first, then Tavily fallback when available."""
    errors: list[str] = []
    try:
        return "ddgs", _ddgs_search(query, max_results=max_results), errors
    except Exception as exc:
        errors.append(f"DDGS error: {exc!s}")

    if os.environ.get("TAVILY_API_KEY"):
        try:
            return (
                "tavily-fallback",
                _tavily_search_results(query, max_results=max_results, topic=topic),
                errors,
            )
        except Exception as exc:
            errors.append(f"Tavily fallback error: {exc!s}")

    return "none", [], errors


async def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    """Fetch and convert webpage content to markdown.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Webpage content as markdown
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return markdownify(response.text)
    except Exception as e:
        return f"Error fetching content from {url}: {e!s}"


@tool(parse_docstring=True)
async def tavily_search(
    query: str,
    max_results: Annotated[int, InjectedToolArg] = 3,
    topic: Annotated[
        Literal["general", "news", "finance"], InjectedToolArg
    ] = "general",
) -> str:
    """Search the web for information on a given query.

    Default backend: DDGS (DuckDuckGo search, no API key required).
    Optional fallback: Tavily when ``TAVILY_API_KEY`` is configured.
    The tool name stays ``tavily_search`` for backward compatibility, but
    new calls should treat it as the project's general web search tool.

    Use one focused query at a time. Prefer short, precise queries over
    repeated retries. If a previous search already failed, change the query
    meaningfully instead of repeating the exact same call.

    Args:
        query: Search query to execute

    Returns:
        Formatted search results with full webpage content in markdown
    """

    try:
        engine, results, errors = await asyncio.to_thread(
            _search_with_fallback,
            query,
            max_results,
            topic,
        )
        if not results:
            joined_errors = "\n".join(errors) if errors else "No search results found."
            return f"Search failed for '{query}'.\n{joined_errors}"

        # Fetch all webpages concurrently. If page fetch fails, fall back to snippet.
        fetch_tasks = [fetch_webpage_content(r["url"]) for r in results]
        contents = await asyncio.gather(*fetch_tasks)

        result_texts = []
        for result, content in zip(results, contents, strict=False):
            rendered_content = content
            if rendered_content.startswith("Error fetching content from"):
                snippet = result.get("snippet", "").strip()
                rendered_content = snippet or rendered_content
            result_text = f"""## {result["title"]}
**URL:** {result["url"]}

{rendered_content}

---
"""
            result_texts.append(result_text)

        errors_block = ""
        if errors:
            errors_block = "\n\nSearch backend notes:\n- " + "\n- ".join(errors)

        return f"""Found {len(result_texts)} result(s) for '{query}' via {engine}:

{"".join(result_texts)}{errors_block}"""

    except Exception as e:
        return f"Search failed: {e!s}"
