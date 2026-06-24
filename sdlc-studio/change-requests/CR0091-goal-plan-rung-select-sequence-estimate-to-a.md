# CR-0091: goal plan rung select sequence estimate to a sprint plan artifact

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

**WS2 of RFC0019. Estimate: 5 points. Depends on CR0087 (rename).** Add the `--goal plan` rung
between `triage` and `design` (RFC0019 D8): from a backlog, **select a sprint-sized batch**
(capacity / budget fit), **sequence** it by dependency, **estimate** it, and emit a persisted
**sprint-plan artifact**, then stop for review. It reuses what exists - `--order wsjf` + the
complexity-weighted budget (CR0038) and `project plan`'s dependency order + wave estimation -
so it is assembly, not new machinery. "Plan the next sprint" resolves here.

## Acceptance Criteria

- [ ] `sprint <batch> --goal plan` selects + sequences + estimates a sprint-sized batch and
      writes a sprint-plan artifact (e.g. `sdlc-studio/.local/sprint-plan.json` + a readable
      summary), then stops for review
- [ ] selection honours capacity/budget; ordering reuses `--order wsjf` + complexity (CR0038)
      and `project plan` dependency/wave logic (no reimplementation)
- [ ] the goal ladder (`triage`/`plan`/`design`/`done`) is documented; NL "plan the next
      sprint" resolves to `--goal plan`
- [ ] unit tests cover selection, sequencing, the artifact shape; CHANGELOG entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
