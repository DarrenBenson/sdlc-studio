# US0800: A bug whose declared mutant was killed by a test its criterion does not name is REPORTED

> **Status:** Draft
> **Closes with:** US0936 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Delivers:** CR0556
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/reference-doctrine.md
> **Epic:** EP0242
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A bug whose declared mutant was killed by a test its criterion does not name is REPORTED
**So that** CR0556 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Ungroomed - acceptance criteria are a grooming placeholder** - author each criterion and its Verify check against this story's slice while grooming, before it is planned to Done. Shape: `templates/core/story.md`. Verifier guidance: `reference-verify.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | backlog sweep 2026-09-15 | Backlog sweep 2026-09-15: checked for supersession and kept open - US0793 would compute killed-elsewhere for bugs too, but nothing wires that verdict into the bug's transition to Fixed: _planned_mutant_gate surfaces only not-run and survived rows. |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0921 ships - planning: SUPERSEDED - mutant killed by unnamed test: mutation ledger deleted in batch 2; superseded only once US0921 ships (D0264) |
| 2026-09-25 | sdlc-studio BG0772 | Closes with re-pointed from US0921 to US0936 (D0264): US0921 was split and US0936 carries the ledger deletion this item waits on |
