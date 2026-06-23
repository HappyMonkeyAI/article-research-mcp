"""RSS/Atom feeds — configurable URLs, query filter."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

import httpx

DEFAULT_FEEDS = (
    "https://dev.to/feed/tag/mcp",
    "https://dev.to/feed/tag/ai",
    "https://hnrss.org/frontpage",
)

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def configured_feeds() -> List[str]:
    raw = os.environ.get("ARTICLE_RESEARCH_RSS_FEEDS", "").strip()
    if raw:
        return [u.strip() for u in raw.split(",") if u.strip()]
    return list(DEFAULT_FEEDS)


def _entry_id(link: str) -> int:
    return abs(hash(link)) % (10**9)


def _parse_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}", value):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except (ValueError, TypeError):
        return None


def _text(el: Optional[ElementTree.Element]) -> str:
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def _parse_feed_xml(body: str, feed_url: str) -> List[Dict[str, Any]]:
    root = ElementTree.fromstring(body)
    entries: List[Dict[str, Any]] = []

    # RSS 2.0
    for item in root.findall(".//item"):
        title = _text(item.find("title"))
        link = _text(item.find("link"))
        desc = _text(item.find("description")) or _text(item.find("{http://purl.org/rss/1.0/modules/content/}encoded"))
        pub = _text(item.find("pubDate")) or _text(item.find("dc:date"))
        entries.append(_normalize_entry(title, link, desc, pub, feed_url))

    # Atom
    for entry in root.findall("atom:entry", ATOM_NS):
        title = _text(entry.find("atom:title", ATOM_NS))
        link_el = entry.find("atom:link[@rel='alternate']", ATOM_NS) or entry.find("atom:link", ATOM_NS)
        link = link_el.get("href", "") if link_el is not None else ""
        desc = _text(entry.find("atom:summary", ATOM_NS)) or _text(entry.find("atom:content", ATOM_NS))
        pub = _text(entry.find("atom:updated", ATOM_NS)) or _text(entry.find("atom:published", ATOM_NS))
        entries.append(_normalize_entry(title, link, desc, pub, feed_url))

    return [e for e in entries if e.get("title") and e.get("url")]


def _normalize_entry(
    title: str,
    link: str,
    description: str,
    published: Optional[str],
    feed_url: str,
) -> Dict[str, Any]:
    link = (link or "").strip()
    return {
        "source": "rss",
        "id": _entry_id(link),
        "title": title.strip(),
        "url": link,
        "description": (description or "")[:2000],
        "tags": ["rss", feed_url],
        "published_at": _parse_date(published),
        "reading_time_minutes": None,
        "public_reactions_count": 0,
        "comments_count": 0,
        "feed_url": feed_url,
    }


async def fetch_feed(feed_url: str) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(feed_url, headers={"User-Agent": "article-research-mcp/0.3"})
        resp.raise_for_status()
    return _parse_feed_xml(resp.text, feed_url)


def _matches_query(entry: Dict[str, Any], query: str) -> bool:
    if not query.strip():
        return True
    hay = f"{entry.get('title', '')} {entry.get('description', '')}".lower()
    words = [w for w in query.lower().split() if len(w) >= 2]
    if not words:
        return True
    return any(w in hay for w in words)


async def search_feeds(
    query: str,
    *,
    feeds: Optional[List[str]] = None,
    limit: int = 20,
    max_entries_per_feed: int = 40,
) -> List[Dict[str, Any]]:
    urls = feeds or configured_feeds()
    collected: List[Dict[str, Any]] = []
    for url in urls:
        try:
            batch = await fetch_feed(url)
        except Exception:
            continue
        for entry in batch[:max_entries_per_feed]:
            if _matches_query(entry, query):
                collected.append(entry)
        if len(collected) >= limit * 2:
            break
    return collected[:limit]


async def get_entry_by_id(article_id: int, feeds: Optional[List[str]] = None) -> Dict[str, Any]:
    urls = feeds or configured_feeds()
    for url in urls:
        try:
            batch = await fetch_feed(url)
        except Exception:
            continue
        for entry in batch:
            if entry.get("id") == article_id:
                out = dict(entry)
                out["body_markdown"] = entry.get("description") or ""
                return out
    raise ValueError(f"RSS entry id {article_id} not found in configured feeds")