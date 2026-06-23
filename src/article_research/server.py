#!/usr/bin/env python3
"""Article research MCP — planning-oriented discovery, briefs, multi-source."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from article_research.pipeline.brief import rank_articles, render_brief_markdown
from article_research.pipeline.dedupe import dedupe_articles
from article_research.pipeline.llm_score import llm_scoring_enabled, score_articles_with_llm
from article_research.planning import (
    build_research_plan,
    format_plan_markdown,
    load_methodology,
)
from article_research.sources import devto as devto_source
from article_research.sources import hn as hn_source
from article_research.sources import rss as rss_source

mcp = FastMCP(
    "article-research-mcp",
    instructions=(
        "Article and tutorial research for agent planning. "
        "Before implementation plans, call plan_article_research then build_topic_brief. "
        "Sources: devto, hn, rss (default devto+hn). RSS feeds via ARTICLE_RESEARCH_RSS_FEEDS. "
        "Optional LLM scoring via OPENAI_COMPAT_* (Ollama). "
        "Depth: quick | standard | deep. Escalate strategic topics to Hermes skill deep-research. "
        "Always return verifiable URLs and article IDs."
    ),
)

SUPPORTED_SOURCES = ("devto", "hn", "rss")
DEFAULT_SOURCES = ["devto", "hn"]


def _slugify(topic: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    return slug[:48] or "topic"


async def _fetch_from_sources(
    query: str,
    sources: List[str],
    *,
    limit: int = 10,
    tag: Optional[str] = None,
    top_days: Optional[int] = None,
) -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    per_source = max(limit, 10)

    for src in sources:
        src = src.strip().lower()
        if src == "devto":
            if tag:
                batch = await devto_source.search_by_tag(
                    tag, per_page=per_source, top_days=top_days or 30
                )
            else:
                batch = await devto_source.search_posts(
                    query,
                    tag=tag,
                    per_page=per_source,
                    top_days=top_days,
                )
            collected.extend(batch)
        elif src == "hn":
            batch = await hn_source.search_stories(query, hits_per_page=per_source)
            collected.extend(batch)
        elif src == "rss":
            batch = await rss_source.search_feeds(query, limit=per_source)
            collected.extend(batch)

    return collected


async def _search_and_rank(
    query: str,
    sources: Optional[List[str]],
    *,
    limit: int = 10,
    tag: Optional[str] = None,
    top_days: Optional[int] = None,
    score_with_llm: bool = False,
) -> List[Dict[str, Any]]:
    srcs = [s.lower() for s in (sources or DEFAULT_SOURCES)]
    for s in srcs:
        if s not in SUPPORTED_SOURCES:
            raise ValueError(f"Unsupported source '{s}'. Supported: {list(SUPPORTED_SOURCES)}")

    raw = await _fetch_from_sources(query, srcs, limit=limit, tag=tag, top_days=top_days)
    deduped = dedupe_articles(raw)
    ranked = rank_articles(deduped, query, hn_boost=len(srcs) > 1)

    if score_with_llm and llm_scoring_enabled():
        ranked = await score_articles_with_llm(ranked, query, max_items=min(8, limit))

    return ranked[: min(limit, 30)]


@mcp.tool()
async def plan_article_research(
    topic: str,
    depth: str = "standard",
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Return a structured research plan for agents (steps, tool order, output paths).
    depth: quick | standard | deep
    """
    plan = build_research_plan(topic, depth=depth, tags=tags)
    plan["plan_markdown"] = format_plan_markdown(plan)
    plan["default_sources"] = DEFAULT_SOURCES
    plan["llm_scoring_available"] = llm_scoring_enabled()
    return plan


@mcp.tool()
async def get_research_methodology() -> str:
    """Full methodology markdown (depth levels, source tiers, checklist)."""
    return load_methodology()


@mcp.tool()
async def search_articles(
    query: str,
    sources: Optional[List[str]] = None,
    limit: int = 10,
    tag: Optional[str] = None,
    top_days: Optional[int] = None,
    score_with_llm: bool = False,
) -> List[Dict[str, Any]]:
    """
    Search article sources (default: devto + hn). Returns unified summaries.
    Set score_with_llm=true when OPENAI_COMPAT_BASE_URL is configured (e.g. Ollama).
    """
    return await _search_and_rank(
        query,
        sources,
        limit=limit,
        tag=tag,
        top_days=top_days,
        score_with_llm=score_with_llm,
    )


@mcp.tool()
async def build_topic_brief(
    topic: str,
    depth: str = "standard",
    limit: int = 12,
    tag: Optional[str] = None,
    sources: Optional[List[str]] = None,
    score_with_llm: bool = False,
) -> Dict[str, Any]:
    """
    Fetch, dedupe, rank articles and return a markdown brief for planning.
    depth=deep enables LLM scoring automatically when OPENAI_COMPAT_* is set.
    """
    use_llm = score_with_llm or (depth == "deep" and llm_scoring_enabled())
    articles = await _search_and_rank(
        topic,
        sources,
        limit=limit,
        tag=tag,
        top_days=30 if depth != "quick" else 7,
        score_with_llm=use_llm,
    )
    md = render_brief_markdown(topic, articles, depth=depth, max_items=limit)
    return {
        "topic": topic,
        "depth": depth,
        "article_count": len(articles),
        "articles": articles,
        "brief_markdown": md,
        "llm_scoring_used": use_llm and llm_scoring_enabled(),
        "sources": sources or DEFAULT_SOURCES,
    }


@mcp.tool()
async def get_article(source: str, article_id: int) -> Dict[str, Any]:
    """Fetch full article body by source and numeric id (devto | hn)."""
    src = source.strip().lower()
    if src == "devto":
        return await devto_source.get_post(article_id)
    if src == "hn":
        return await hn_source.get_story(article_id)
    if src == "rss":
        return await rss_source.get_entry_by_id(article_id)
    raise ValueError(f"Unsupported source '{source}'. Use: devto, hn, rss")


@mcp.tool()
async def save_research_note(
    topic: str,
    content_markdown: str,
    slug: Optional[str] = None,
    filename: str = "ARTICLE_BRIEF.md",
) -> Dict[str, Any]:
    """Persist a research note under ~/research/<slug>/ (creates dirs)."""
    research_root = Path(os.environ.get("ARTICLE_RESEARCH_ROOT", Path.home() / "research"))
    use_slug = slug or _slugify(topic)
    out_dir = (research_root / use_slug).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    header = f"# {topic}\n\n_Saved by article-research-mcp_\n\n"
    out_path.write_text(header + content_markdown.strip() + "\n", encoding="utf-8")
    return {"path": str(out_path), "slug": use_slug, "bytes": out_path.stat().st_size}


@mcp.tool()
def list_article_sources() -> Dict[str, Any]:
    """List supported sources and whether LLM scoring is configured."""
    return {
        "sources": list(SUPPORTED_SOURCES),
        "default": DEFAULT_SOURCES,
        "llm_scoring_enabled": llm_scoring_enabled(),
        "rss_feeds": rss_source.configured_feeds(),
    }


@mcp.resource("article-research://methodology")
async def methodology_resource() -> str:
    return load_methodology()


@mcp.resource("article-research://plan/{topic}")
async def plan_resource(topic: str) -> str:
    plan = build_research_plan(topic, depth="standard")
    return format_plan_markdown(plan)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()