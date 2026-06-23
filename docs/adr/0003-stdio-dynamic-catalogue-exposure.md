# ADR 0003: stdio + Dynamic MCP catalogue exposure

- **Status:** accepted
- **Date:** 2026-06-21

## Context

Hermes and Antigravity load MCP servers via stdio or HTTP. The **DynamicMCPProxy** lazy-mounts catalogue entries by project tags; stdout must stay clean.

## Decision

- Run as **stdio** FastMCP: `uv --directory <repo> run article-research-mcp`
- Catalogue name: **`article_research`** (underscore for Antigravity tool rules)
- Register in **launcher-project-registry** with `transport: stdio`, no ports
- Optional direct `hermes mcp add` for always-on tools

## Consequences

- No built-in HTTP health URL; health = process + tool smoke tests.
- Proxy must reload catalogue after JSON edits.

## Alternatives considered

- HTTP/SSE-only server — rejected (extra port management vs proxy stdio mounting).
- Only Hermes register — rejected (Antigravity users need catalogue).