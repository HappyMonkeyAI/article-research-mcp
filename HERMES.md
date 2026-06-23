# HERMES.md — article-research-mcp

Agent quick reference (Hermes / Antigravity / CLI).

## Before coding

1. Read `CONTEXT.md` and relevant `docs/adr/*.md`
2. `uv sync` in repo root; run `uv run pytest`
3. Smoke: `uv run article-research-mcp` (stdio — test via inspect or integration client)

## Tool naming

Catalogue / proxy: **`article_research`** (underscores). Hermes native tools may appear as `mcp_article_research_*`.

## Common tasks

```bash
uv run pytest -q
uv run python scripts/daily_brief.py
```

## Cross-repo

- **DynamicMCPProxy** — edit `catalogue.json` for env_vars / command
- **launcher-project-registry** — `article-research-mcp` slug; use launcher MCP to query ports (this project has no HTTP port)
- **user-context-mcp** — `context/repos.md` points here for planning MCP

## Documentation duty

Architecture or source-adapter changes → new or updated ADR + `CONTEXT.md` summary table.