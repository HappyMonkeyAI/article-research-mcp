#!/usr/bin/env python3
"""Daily article briefs → ~/research/daily-briefs/ (for cron / no_agent)."""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow `uv run python scripts/daily_brief.py` from project root
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from article_research.server import build_topic_brief, save_research_note  # noqa: E402


def _topics() -> list[str]:
    raw = os.environ.get("ARTICLE_DAILY_TOPICS", "model context protocol, ai agents planning")
    return [t.strip() for t in raw.split(",") if t.strip()]


async def main() -> int:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_lines: list[str] = []
    any_saved = False

    for topic in _topics():
        brief = await build_topic_brief(topic, depth="standard", limit=8)
        if brief.get("article_count", 0) == 0:
            continue
        slug = f"daily-briefs/{day}-{topic[:30].lower().replace(' ', '-')}"
        saved = await save_research_note(
            topic=f"Daily brief {day}: {topic}",
            content_markdown=brief["brief_markdown"],
            slug=slug,
            filename="BRIEF.md",
        )
        any_saved = True
        out_lines.append(f"{topic}: {brief['article_count']} articles → {saved['path']}")

    if not any_saved:
        return 0
    print(f"Article research daily ({day})")
    for line in out_lines:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))