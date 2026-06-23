# Article research methodology (for agents)

Use this MCP when **planning** implementation, comparing libraries, or gathering practitioner write-ups — before writing code or a long-form plan.

## Depth levels

| Depth | Time | MCP path | Escalate to Hermes |
|-------|------|----------|-------------------|
| **quick** | ~15 min | `search_articles` + skim top 3 `get_article` | — |
| **standard** | ~1–2 hr | `plan_article_research` → `build_topic_brief` | Optional: `deep-research` skill for 3 lenses |
| **deep** | half day+ | Brief + saved note under `~/research/<slug>/` | Load `deep-research` skill; all 9 lenses |

## Source tiers (align with deep-research)

1. **Primary** — official docs, repo README, release notes
2. **Expert** — long tutorials with working code, maintainer posts
3. **Commentary** — dev.to / HN discussion with reproducible steps
4. **General** — news summaries (verify upstream)
5. **Social** — anecdotes only; use for signals, not conclusions

## Planning checklist

1. Call `plan_article_research(topic, depth)` at task start.
2. Run `build_topic_brief` for a deduped reading list (sources: **devto**, **hn**).
3. `get_article` for 2–5 full bodies that match your stack.
4. Record open questions; if strategic, hand off to `deep-research`.
5. Return **URLs and article IDs** in summaries — verifiable handles.

## Outputs

- In-session: markdown brief from `build_topic_brief`
- Durable: `save_research_note` → `~/research/<slug>/ARTICLE_BRIEF.md`