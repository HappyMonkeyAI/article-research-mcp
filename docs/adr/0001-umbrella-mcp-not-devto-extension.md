# ADR 0001: Umbrella planning MCP separate from devto-mcp-server

- **Status:** accepted
- **Date:** 2026-06-21

## Context

`devto-mcp-server` exposed three focused tools (search, get article, tag search). Planning workflows needed dedupe, ranked briefs, methodology, multi-source fetch, and disk handoff to `~/research/` — overlapping with Horizon-style radar patterns but scoped to **agent planning**, not daily news digests.

## Decision

Create **article-research-mcp** as the umbrella planning server. Keep **devto-mcp-server** thin; catalogue retains a `devto` lite entry; README points planners to `article_research`.

## Consequences

- Two codepaths may share httpx patterns; duplication is acceptable until a shared `devto-client` package is justified.
- Agents must load `article-research-planning` skill or MCP instructions to use the right server.

## Alternatives considered

- Extend devto-mcp-server with brief tools — rejected (bloat, wrong catalogue tags for HN/RSS).
- Single monolithic “research” server including full deep-research — rejected (token cost, overlap with Hermes skill).