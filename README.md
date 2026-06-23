# article-research-mcp

MCP server for **article/tutorial research during agent planning** — dev.to search, deduped ranked briefs, methodology aligned with Hermes `deep-research`.

**Agent docs:** `CONTEXT.md`, `HERMES.md`, `docs/adr/`, `research/`

## Sources (v0.2)

| Source | Id |
|--------|-----|
| dev.to | `devto` |
| Hacker News (Algolia) | `hn` |
| RSS/Atom (configurable) | `rss` |

Default: **devto + hn**. Add `rss` via `sources=["devto","hn","rss"]`.

**RSS feeds** — `ARTICLE_RESEARCH_RSS_FEEDS` (comma-separated URLs) or built-in defaults (dev.to mcp/ai tags, hnrss frontpage).

## LLM scoring (optional)

Set OpenAI-compatible API (e.g. LAN Ollama):

```bash
export OPENAI_COMPAT_BASE_URL=http://localhost:11434/v1
export OPENAI_COMPAT_API_KEY=ollama
export OPENAI_COMPAT_MODEL=lfm2.5:latest
```

- `search_articles(..., score_with_llm=true)`
- `build_topic_brief(..., depth=deep)` auto-enables LLM scoring when env is set

Without env vars, deterministic ranking only.

## Tools

| Tool | Purpose |
|------|---------|
| `plan_article_research` | Step list + tool sequence for quick/standard/deep |
| `get_research_methodology` | Depth levels, source tiers, checklist |
| `search_articles` | Multi-source search (devto + hn) |
| `build_topic_brief` | Dedupe + rank + markdown brief |
| `get_article` | Full body by `source` + `id` |
| `save_research_note` | Write `~/research/<slug>/ARTICLE_BRIEF.md` |
| `list_article_sources` | Supported sources + LLM config status |

## Resources

- `article-research://methodology`
- `article-research://plan/{topic}`

## Daily briefs (cron)

```bash
ARTICLE_DAILY_TOPICS="mcp,agent planning" uv run python scripts/daily_brief.py
```

Writes `~/research/daily-briefs/<date>-<topic>/BRIEF.md`. Hermes cron: `research/daily_article_brief.sh` at **08:00 UTC** (job `6ab3a0a34eb2`), delivers summary to this Slack DM when stdout is non-empty.

## Run locally

```bash
cd /path/to/article-research-mcp
uv sync
uv run article-research-mcp
```

## Dynamic MCP Proxy (`catalogue.json`)

Entry name: `article_research` (see DynamicMCPProxy `catalogue.json`).

## Hermes (optional direct register)

```bash
cd /path/to/article-research-mcp
uv sync
printf 'y\n' | hermes mcp add article_research \
  --command uv \
  --args --directory,/path/to/article-research-mcp,run,article-research-mcp
```

New session or `/reload-mcp` + `/reset`.

## Env

| Variable | Default |
|----------|---------|
| `ARTICLE_RESEARCH_ROOT` | `~/research` |
| `OPENAI_COMPAT_BASE_URL` | — (e.g. `http://localhost:11434/v1`) |
| `OPENAI_COMPAT_API_KEY` | `ollama` |
| `OPENAI_COMPAT_MODEL` | `lfm2.5:latest` |

## Related

- `devto-mcp-server` — thin dev.to-only server (superseded for planning use this umbrella)
- Hermes skill `deep-research` — multi-lens synthesis after briefs

## License

MIT