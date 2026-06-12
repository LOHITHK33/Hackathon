from __future__ import annotations

import asyncio

from ddgs import DDGS


def _search_sync(query: str, max_results: int = 5) -> list[dict]:
    try:
        with DDGS() as ddgs:
            hits = ddgs.text(query, max_results=max_results)
            return [
                {
                    "title": h.get("title", ""),
                    "url": h.get("href", ""),
                    "snippet": h.get("body", ""),
                }
                for h in hits
            ]
    except Exception as exc:
        return [{"title": "search unavailable", "url": "", "snippet": str(exc)}]


async def web_search(query: str, max_results: int = 5) -> list[dict]:
    return await asyncio.to_thread(_search_sync, query, max_results)


def format_results(results: list[dict]) -> str:
    if not results:
        return "No results found."
    blocks = []
    for i, r in enumerate(results, 1):
        blocks.append(f"[{i}] {r['title']}\n{r['snippet']}\n{r['url']}")
    return "\n\n".join(blocks)