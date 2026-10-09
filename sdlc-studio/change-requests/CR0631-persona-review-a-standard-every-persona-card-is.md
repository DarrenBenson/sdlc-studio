# CR-0631: Persona review: a standard every persona card is held to, and an independent review that blocks a failing card

> **Status:** Proposed
> **Parent:** RFC0061
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** .claude/skills/sdlc-studio/best-practices/persona.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/help/persona.md
> **Priority:** High
> **Type:** Feature
> **Size:** L

## Summary

RFC0061 workstream 1 (D7). Define the persona standard (format, evidence for every claim, testable goals, consistency with the declared cast and the other seats, freshness) as a best-practices page, implement it as validate checks, and add a persona review ceremony: an independent seat reviews a new or changed card against the standard, and a card that fails it cannot be resolved into a brief until fixed. Memory problems are reported, not blocked. Runs on every card change and once per release. Folds in CR0623 and CR0625's checks (EP0285) as rules this standard cites; they keep their names.

## Acceptance Criteria

- [ ] A new or changed persona card that fails the standard is refused by `persona_resolve` until fixed, naming each failed rule
- [ ] The persona review runs on every card change and once per release, recorded with the reviewing seat and the outcome

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Created via `new` (deterministic) |
