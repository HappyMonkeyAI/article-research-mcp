"""Deduplicate articles across sources by URL and normalized title."""

from __future__ import annotations

import re
from typing import Any, Dict, List
from urllib.parse import urlparse


def _norm_title(title: str) -> str:
    t = (title or "").lower().strip()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _norm_url(url: str) -> str:
    if not url:
        return ""
    p = urlparse(url.strip())
    path = p.path.rstrip("/")
    return f"{p.netloc.lower()}{path}"


def dedupe_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_url: set[str] = set()
    seen_title: set[str] = set()
    out: List[Dict[str, Any]] = []

    for item in articles:
        url_key = _norm_url(str(item.get("url") or ""))
        title_key = _norm_title(str(item.get("title") or ""))

        if url_key and url_key in seen_url:
            continue
        if title_key and len(title_key) > 12 and title_key in seen_title:
            continue

        if url_key:
            seen_url.add(url_key)
        if title_key:
            seen_title.add(title_key)
        out.append(item)

    return out