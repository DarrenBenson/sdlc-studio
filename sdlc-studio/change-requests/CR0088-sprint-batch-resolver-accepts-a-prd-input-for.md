# CR-0088: sprint batch resolver accepts a PRD input for the authoring bootstrap

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

**WS1 of RFC0019. Estimate: 3 points. Depends on CR0087 (rename).** Teach `sprint`'s batch
resolver to accept a **PRD path** as the batch source (`sprint <prd.md>`), routing to the
authoring bootstrap, alongside the existing `--bugs`/`--crs`/`--stories`/`--epic` queries.
This is the one thing the loop cannot do today (its input is always an existing backlog), and
the gap RFC0019 closes (D1: extend, don't fork).

## Acceptance Criteria

- [ ] `sprint <prd.md>` is recognised as a PRD-input batch and selects "authoring" mode (the
      planner reports the mode); a missing/invalid PRD path fails fast with a clear message
- [ ] the existing query inputs (`--bugs`/`--crs`/`--stories`/`--epic`) are unchanged
- [ ] NL resolves a PRD-shaped request (e.g. "plan a sprint from the PRD") to this path
      (RFC0001 NL-to-goal resolution, extended)
- [ ] unit tests cover: PRD input selected, bad path rejected, query inputs untouched;
      CHANGELOG `[Unreleased]` entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
