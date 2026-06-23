"""Planning templates for agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
METHODOLOGY_PATH = ROOT / "context" / "methodology.md"

DEPTH_STEPS: Dict[str, List[str]] = {
    "quick": [
        "Call search_articles with limit 5.",
        "get_article for the best match only.",
        "Summarize 3 bullets for the plan; no file write required.",
    ],
    "standard": [
        "Call plan_article_research (this plan).",
        "build_topic_brief with limit 10–15.",
        "get_article for top 3–5 results.",
        "Optional: save_research_note to ~/research/<slug>/ARTICLE_BRIEF.md.",
    ],
    "deep": [
        "build_topic_brief then full get_article passes on top 5.",
        "save_research_note with open questions section.",
        "Load Hermes skill deep-research; seed with this brief.",
        "Produce ~/research/<slug>/RESEARCH.md handoff per deep-research skill.",
    ],
}


def load_methodology() -> str:
    if METHODOLOGY_PATH.is_file():
        return METHODOLOGY_PATH.read_text(encoding="utf-8")
    return "(methodology.md missing)"


def build_research_plan(topic: str, depth: str = "standard", tags: List[str] | None = None) -> Dict[str, Any]:
    depth = depth.strip().lower()
    if depth not in DEPTH_STEPS:
        depth = "standard"

    tag_hint = tags or []
    slug = "-".join(w for w in topic.lower().split() if w.isalnum() or w == "-")[:48] or "topic"

    return {
        "topic": topic,
        "depth": depth,
        "suggested_tags": tag_hint,
        "output_dir": f"~/research/{slug}/",
        "steps": DEPTH_STEPS[depth],
        "mcp_tools_sequence": [
            "plan_article_research",
            "search_articles",
            "build_topic_brief",
            "get_article",
            "save_research_note (standard/deep)",
        ],
        "hermes_escalation": "skill: deep-research" if depth == "deep" else "optional",
        "methodology_excerpt": load_methodology()[:1200],
    }


def format_plan_markdown(plan: Dict[str, Any]) -> str:
    lines = [
        f"# Research plan: {plan['topic']}",
        "",
        f"**Depth:** {plan['depth']}",
        f"**Suggested output:** `{plan['output_dir']}`",
        "",
        "## Steps",
        "",
    ]
    for i, step in enumerate(plan["steps"], start=1):
        lines.append(f"{i}. {step}")
    lines.extend(["", "## Tool sequence", ""])
    for t in plan["mcp_tools_sequence"]:
        lines.append(f"- `{t}`")
    lines.extend(["", f"**Hermes escalation:** {plan['hermes_escalation']}", ""])
    return "\n".join(lines)