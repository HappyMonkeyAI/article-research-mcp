"""Optional LLM relevance scoring (OpenAI-compatible, e.g. Ollama)."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import httpx

DEFAULT_TIMEOUT = 60.0


def llm_scoring_enabled() -> bool:
    return bool(os.environ.get("OPENAI_COMPAT_BASE_URL", "").strip())


def _llm_config() -> Dict[str, str]:
    base = os.environ.get("OPENAI_COMPAT_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("OPENAI_COMPAT_API_KEY", "ollama")
    model = os.environ.get("OPENAI_COMPAT_MODEL", "lfm2.5:latest")
    return {"base_url": base, "api_key": api_key, "model": model}


def _parse_scores_json(text: str) -> Dict[str, float]:
    """Extract id->score map from model output."""
    text = text.strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    out: Dict[str, float] = {}
    for k, v in data.items():
        try:
            out[str(k)] = float(v)
        except (TypeError, ValueError):
            continue
    return out


async def score_articles_with_llm(
    articles: List[Dict[str, Any]],
    topic: str,
    *,
    max_items: int = 8,
) -> List[Dict[str, Any]]:
    """
    Add llm_relevance_score (0-10) to articles. Falls back silently if LLM unavailable.
    """
    if not llm_scoring_enabled():
        return articles

    cfg = _llm_config()
    batch = articles[:max_items]
    if not batch:
        return articles

    lines = []
    for a in batch:
        aid = a.get("id")
        title = a.get("title", "")
        desc = (a.get("description") or "")[:300]
        lines.append(f"- id={aid} | {title} | {desc}")

    prompt = (
        f"Topic for a software planning research brief: {topic}\n\n"
        "Rate each item 0-10 for usefulness to an engineer planning implementation "
        "(not hype). Return ONLY JSON: {\"<id>\": <score>, ...}\n\n"
        + "\n".join(lines)
    )

    url = f"{cfg['base_url']}/chat/completions"
    headers = {"Authorization": f"Bearer {cfg['api_key']}"}
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        scores = _parse_scores_json(content)
    except Exception:
        return articles

    merged: List[Dict[str, Any]] = []
    for a in articles:
        copy = dict(a)
        key = str(a.get("id"))
        if key in scores:
            copy["llm_relevance_score"] = round(scores[key], 2)
            det = copy.get("relevance_score") or 0
            copy["relevance_score"] = round(det * 0.4 + scores[key] * 0.6, 2)
        merged.append(copy)

    merged.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return merged