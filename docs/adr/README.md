# Architecture Decision Records (ADR)

Durable decisions for **article-research-mcp**. Format aligned with repo `setup-prompt.txt` / ai-agent-teamwork-prompt conventions.

## When to write an ADR

- New article source adapter or removal
- Ranking/scoring pipeline change
- MCP tool contract change agents depend on
- Splitting or merging MCP servers

## File naming

`NNNN-short-title.md` — four-digit sequence, kebab-case slug.

## Template

```markdown
# ADR NNNN: Title

- **Status:** accepted | superseded | deprecated
- **Date:** YYYY-MM-DD

## Context

What problem or constraint forced a decision?

## Decision

What we chose.

## Consequences

Positive, negative, and follow-ups.

## Alternatives considered

Brief list.
```

## Index

| ADR | Title |
|-----|--------|
| [0001](0001-umbrella-mcp-not-devto-extension.md) | Umbrella planning MCP separate from devto-mcp-server |
| [0002](0002-deterministic-rank-with-optional-llm.md) | Deterministic rank + optional LLM scoring |
| [0003](0003-stdio-dynamic-catalogue-exposure.md) | stdio + Dynamic MCP catalogue exposure |