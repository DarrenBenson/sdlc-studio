# CR-0632: Seat memory: each persona keeps a committed memory file of evidenced learnings, carried into its own brief

> **Status:** Proposed
> **Parent:** RFC0061
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/personas/memory-template.md, .claude/skills/sdlc-studio/reference-persona.md
> **Priority:** High
> **Type:** Feature
> **Size:** L

## Summary

RFC0061 workstream 2 (D1, D5, D8). A memory file beside each card (`sdlc-studio/personas/memory/<persona>.md`), committed, owned by a tool (`persona_memory.py add | list | recall | revalidate | prune`). Each learning carries its evidence (ledger rows, rulings, findings), a date and a validity horizon, revalidated or retired as project lessons are. `persona_resolve` injects the persona's top learnings (capped, ranked by recency and relevance) into that persona's own brief, beside the project lessons it already gets.

## Acceptance Criteria

- [ ] A persona's brief carries its own approved learnings, capped and ranked, and never another persona's
- [ ] A learning past its horizon is reported at the close until it is revalidated or retired

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Created via `new` (deterministic) |
