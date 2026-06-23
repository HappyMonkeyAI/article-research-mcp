"""Hacker News search via Algolia API + item fetch via Firebase API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

ALGOLIA_SEARCH = "https://hn.algolia.com/api/v1/search"
HN_ITEM_API = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"


async def fetch_json(url: str, params: Optional[Dict[str, Any]] = None) -> Any:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


def normalize_hit(hit: Dict[str, Any]) -> Dict[str, Any]:
    created = hit.get("created_at_i") or hit.get("created_at")
    published_at = None
    if isinstance(created, (int, float)):
        published_at = datetime.fromtimestamp(created, tz=timezone.utc).isoformat()
    elif isinstance(created, str):
        published_at = created

    story_id = hit.get("objectID") or hit.get("id")
    title = hit.get("title") or hit.get("story_title") or ""
    url = hit.get("url") or hit.get("story_url") or ""
    if not url and story_id:
        url = f"https://news.ycombinator.com/item?id={story_id}"

    desc = (hit.get("story_text") or hit.get("comment_text") or hit.get("_tags") or "")
    if isinstance(desc, list):
        desc = " ".join(desc)
    desc = str(desc)[:500]

    return {
        "source": "hn",
        "id": int(story_id) if story_id is not None else None,
        "title": title,
        "url": url,
        "description": desc,
        "tags": ["hackernews"],
        "published_at": published_at,
        "reading_time_minutes": None,
        "public_reactions_count": hit.get("points") or 0,
        "comments_count": hit.get("num_comments") or 0,
        "user": hit.get("author"),
        "raw": hit,
    }


async def search_stories(
    query: str,
    *,
    hits_per_page: int = 15,
    page: int = 0,
) -> List[Dict[str, Any]]:
    params = {
        "query": query,
        "tags": "story",
        "hitsPerPage": min(hits_per_page, 50),
        "page": page,
    }
    data = await fetch_json(ALGOLIA_SEARCH, params)
    hits = data.get("hits") or []
    return [normalize_hit(h) for h in hits if h.get("title") or h.get("story_title")]


async def get_story(item_id: int) -> Dict[str, Any]:
    url = HN_ITEM_API.format(item_id=item_id)
    raw = await fetch_json(url)
    if not raw:
        raise ValueError(f"HN item {item_id} not found")

    hit = {
        "objectID": raw.get("id"),
        "title": raw.get("title"),
        "url": raw.get("url"),
        "story_text": raw.get("text"),
        "points": raw.get("score"),
        "num_comments": len(raw.get("kids") or []),
        "author": raw.get("by"),
        "created_at_i": raw.get("time"),
    }
    out = normalize_hit(hit)
    body_parts = []
    if raw.get("text"):
        body_parts.append(raw["text"])
    if raw.get("url"):
        body_parts.append(f"\n\nLink: {raw['url']}")
    out["body_markdown"] = "\n".join(body_parts).strip()
    out["raw_item"] = raw
    return out