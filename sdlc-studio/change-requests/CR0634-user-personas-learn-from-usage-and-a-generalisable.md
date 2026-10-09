# CR-0634: User personas learn from usage, and a generalisable persona learning can be promoted to the shipped amigos

> **Status:** Proposed
> **Parent:** RFC0061
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/personas/amigos/, .claude/skills/sdlc-studio/reference-persona.md
> **Priority:** Medium
> **Type:** Feature
> **Size:** M

## Summary

RFC0061 workstream 4 (D6, D9). After seat memory: user personas (Maya, Jonah, Trevor) keep memory from usage evidence, starting with served-goal outcomes (CR0629, running a persona's testable End goal at the close) and stakeholder feedback (RFC0058). A generalisable learning can be promoted to the skill's shipped amigo cards by a deliberate act through the skill source repository, as `lessons add --global` promotes a lesson, never automatically.

## Acceptance Criteria

- [ ] A user persona's memory records a served-goal outcome as evidence with its run
- [ ] Promoting a persona learning writes only to the skill source checkout and is refused into an installed copy

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Created via `new` (deterministic) |
