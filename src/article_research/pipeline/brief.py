"""Rank articles and render planning briefs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def score_article(article: Dict[str, Any], topic: str) -> float:
    """Deterministic rank (v0). Higher = more relevant for planning."""
    topic_l = topic.lower()
    title = (article.get("title") or "").lower()
    desc = (article.get("description") or "").lower()
    tags = [str(t).lower() for t in (article.get("tags") or [])]

    score = 0.0
    for word in topic_l.split():
        if len(word) < 3:
            continue
        if word in title:
            score += 4.0
        if word in desc:
            score += 1.5
        if word in tags:
            score += 3.0

    score += min((article.get("public_reactions_count") or 0) / 10.0, 5.0)
    score += min((article.get("comments_count") or 0) / 5.0, 5.0)

    published = _parse_dt(article.get("published_at"))
    if published:
        age_days = (datetime.now(timezone.utc) - published.astimezone(timezone.utc)).days
        if age_days <= 30:
            score += 3.0
        elif age_days <= 180:
            score += 1.0

    return round(score, 2)


def rank_articles(
    articles: List[Dict[str, Any]],
    topic: str,
    *,
    hn_boost: bool = False,
) -> List[Dict[str, Any]]:
    ranked = []
    for a in articles:
        copy = dict(a)
        score = score_article(a, topic)
        if hn_boost and a.get("source") == "hn":
            score += 0.5
        copy["relevance_score"] = score
        ranked.append(copy)
    ranked.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return ranked


def render_brief_markdown(
    topic: str,
    articles: List[Dict[str, Any]],
    *,
    depth: str = "standard",
    max_items: int = 10,
) -> str:
    lines = [
        f"# Article research brief: {topic}",
        "",
        f"**Depth:** {depth} | **Items:** {min(len(articles), max_items)}",
        "",
        "## Reading list (deduped, ranked)",
        "",
    ]
    for i, a in enumerate(articles[:max_items], start=1):
        score = a.get("relevance_score", "")
        llm = a.get("llm_relevance_score")
        score_note = f"score {score}" + (f", llm {llm}" if llm is not None else "")
        tags = ", ".join(a.get("tags") or []) or "—"
        lines.append(
            f"{i}. **{a.get('title', '(no title)')}** ({score_note})  \n"
            f"   - URL: {a.get('url', '')}  \n"
            f"   - Source: {a.get('source')} id={a.get('id')}  \n"
            f"   - Tags: {tags}  \n"
            f"   - {a.get('description', '')[:200]}"
        )
        lines.append("")

    lines.extend(
        [
            "## Suggested next steps",
            "",
            "1. `get_article` on top 2–3 IDs for full markdown bodies.",
            "2. Note stack-specific gaps as open questions.",
            "3. Escalate to Hermes `deep-research` skill if the decision is strategic.",
            "",
        ]
    )
    return "\n".join(lines)