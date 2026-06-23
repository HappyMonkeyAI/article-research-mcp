# ADR 0002: Deterministic rank with optional LLM scoring

- **Status:** accepted
- **Date:** 2026-06-21

## Context

Horizon and similar radars use LLM scoring for every item. Planning MCP must work offline and in CI without GPU; LAN Ollama is optional.

## Decision

- **v0/v1 default:** `score_article()` heuristic (title/description/tags/recency/reactions).
- **Optional:** `OPENAI_COMPAT_*` env → `score_articles_with_llm()` blends 40% heuristic / 60% LLM for top N items.
- **Trigger:** `score_with_llm=true` or `depth=deep` when env configured.

## Consequences

- Rankings differ per environment; document env in brief metadata when LLM used.
- Failed LLM calls fail open (deterministic only).

## Alternatives considered

- Mandatory Ollama — rejected for portability.
- Embeddings-only rank — deferred (v2).