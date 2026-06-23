# CONTEXT — article-research-mcp

Operating manual for agents and contributors. Source of truth alongside `docs/adr/`.

## Stack & runtime

- **Python** ≥ 3.10, **uv** for env and runs
- **FastMCP** stdio server (`article-research-mcp` entrypoint)
- **httpx** for dev.to, HN Algolia, RSS fetch
- **No embedded DB** — stateless per request; notes on disk under `ARTICLE_RESEARCH_ROOT` (default `~/research`)

## Non-negotiable rules

1. **stdio discipline** — no stray stdout; `mcp.run(show_banner=False, log_level="WARNING")`
2. **Thin domain servers** — do not fold planning/dedupe/brief logic into `devto-mcp-server`
3. **Verifiable outputs** — tools return URLs and numeric `id` + `source` for every article
4. **Hermes escalation** — strategic synthesis stays in skill `deep-research`, not duplicated here
5. **Secrets** — optional LLM via env only; never commit API keys

## Workflow

- Planning agents: `plan_article_research` → `build_topic_brief` → `get_article` (see skill `article-research-planning`)
- Implementation plans: load `writing-plans` after brief exists
- Doc changes: update **CONTEXT.md** and **ADRs** in the same PR when architecture shifts
- Daily briefs: `scripts/daily_brief.py` / Hermes `research/daily_article_brief.sh`

## Resolved decisions (summary)

| Topic | Decision |
|-------|----------|
| Umbrella MCP | Separate repo; dev.to remains thin alias in catalogue |
| Ranking v0 | Deterministic score; optional OpenAI-compatible LLM blend |
| Sources | devto + hn default; rss opt-in; adapters in `src/article_research/sources/` |
| Gateway | Dynamic MCP catalogue name `article_research` |
| Registry | Listed in launcher-project-registry with `transport: stdio` |

Details: `docs/adr/`.

## Exposure

| Channel | How |
|---------|-----|
| Dynamic MCP Proxy | `catalogue.json` → `article_research` |
| Hermes | `hermes mcp add` + uv command (optional) |
| Launcher registry | slug `article-research-mcp` |

## What not to do

- Do not add heavy in-MCP multi-lens research (use Hermes `deep-research`)
- Do not break unified article dict shape across sources without an ADR
- Do not register duplicate catalogue servers for the same planning surface
- Do not use `feedparser`/heavy deps without justification (stdlib RSS parser for v0.3)

## Paths

| Path | Role |
|------|------|
| `context/methodology.md` | MCP resource + `get_research_methodology` |
| `src/article_research/server.py` | Tools |
| `scripts/daily_brief.py` | Cron driver |
| `research/` | External references (Horizon, etc.) |