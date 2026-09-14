# US0719: A sprint closes WITH open defects as the normal case, needing no waiver

> **Status:** Superseded
> **Superseded by:** US0571, CR0506
> **Delivers:** CR0507
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-doctrine.md
> **Epic:** EP0224
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A sprint closes WITH open defects as the normal case, needing no waiver
**So that** CR0507 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Ungroomed - acceptance criteria are a grooming placeholder** - author each criterion and its Verify check against this story's slice while grooming, before it is planned to Done. Shape: `templates/core/story.md`. Verifier guidance: `reference-verify.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | backlog sweep 2026-09-15 | Backlog sweep 2026-09-15: superseded by US0571 (Done) with CR0506 (Complete). A close already carries ruled open defects with no waiver as the normal case: close_preflight holds only on an unruled finding or a stop-ship ruling, close_goal_judgement reports and never refuses, no waiver has been recorded since D0171, and RETRO0116 carried 27+ ruled open items. Proposed by a sweep agent, confirmed by an independent adversarial verifier. |
