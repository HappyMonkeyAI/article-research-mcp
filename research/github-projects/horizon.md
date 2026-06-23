# Thysrael/Horizon

- **URL:** https://github.com/Thysrael/Horizon
- **License:** MIT
- **Stack:** Python, multi-source fetch, LLM scoring, briefings
- **Why it matters:** Inspiration for article **pipeline** (not memory). ~6.7k stars; active 2026.
- **Cherry-pick:** dedupe + score + deliver brief; separate cron digest option
- **Avoid:** Treating as agent long-term memory; full news-radar scope inside planning MCP
- **Date reviewed:** 2026-06-21

## Relation to article-research-mcp

We took **pattern only**: unified fetch → dedupe → rank → markdown brief. Horizon's always-on LLM score became optional `OPENAI_COMPAT_*` in ADR 0002.