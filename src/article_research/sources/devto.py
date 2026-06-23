"""dev.to API adapter."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

DEVTO_API_BASE = "https://dev.to/api"


async def fetch_json(url: str, params: Optional[Dict[str, Any]] = None) -> Any:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


def normalize_article(raw: Dict[str, Any], source: str = "devto") -> Dict[str, Any]:
    """Unified article record for pipeline code."""
    return {
        "source": source,
        "id": raw.get("id"),
        "title": raw.get("title") or "",
        "url": raw.get("url") or "",
        "description": raw.get("description") or "",
        "tags": raw.get("tag_list") or raw.get("tags") or [],
        "published_at": raw.get("published_at") or raw.get("published_timestamp"),
        "reading_time_minutes": raw.get("reading_time_minutes"),
        "public_reactions_count": raw.get("public_reactions_count") or 0,
        "comments_count": raw.get("comments_count") or 0,
        "user": (raw.get("user") or {}).get("username"),
        "raw": raw,
    }


async def search_posts(
    query: str,
    *,
    tag: Optional[str] = None,
    per_page: int = 10,
    page: int = 1,
    top_days: Optional[int] = None,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "per_page": min(per_page, 30),
        "page": page,
    }
    if top_days:
        params["top"] = top_days
        if tag:
            params["tag"] = tag.lower()
    else:
        params["search"] = query
        if tag:
            params["tag"] = tag

    url = f"{DEVTO_API_BASE}/articles"
    articles = await fetch_json(url, params)
    if not isinstance(articles, list):
        return []
    return [normalize_article(a) for a in articles]


async def get_post(article_id: int) -> Dict[str, Any]:
    url = f"{DEVTO_API_BASE}/articles/{article_id}"
    raw = await fetch_json(url)
    out = normalize_article(raw)
    out["body_markdown"] = raw.get("body_markdown") or ""
    return out


async def search_by_tag(
    tech: str,
    *,
    per_page: int = 15,
    top_days: Optional[int] = 30,
) -> List[Dict[str, Any]]:
    return await search_posts(
        query=tech,
        tag=tech.lower(),
        per_page=per_page,
        top_days=top_days,
    )