# US0814: The floor lane is bound into the pre-commit gate, so it runs in the command people actually run

> **Status:** Superseded
> **Superseded by:** US0908 - US0908 runs the floor check once per push in CI; binding a lane into pre-commit would add to the 90s commit budget, which LC-008 and the Sprint 3 goal rule out
> **Delivers:** CR0561
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, tools/tests/test_check_python_floor.py
> **Epic:** EP0246
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The floor lane is bound into the pre-commit gate, so it runs in the command people actually run
**So that** CR0561 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Ungroomed - acceptance criteria are a grooming placeholder** - author each criterion and its Verify check against this story's slice while grooming, before it is planned to Done. Shape: `templates/core/story.md`. Verifier guidance: `reference-verify.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Superseded by US0908 (RUN-01M39MC0): US0908 runs the floor check once per push in CI; binding a lane into pre-commit would add to the 90s commit budget, which LC-008 and the Sprint 3 goal rule out |
