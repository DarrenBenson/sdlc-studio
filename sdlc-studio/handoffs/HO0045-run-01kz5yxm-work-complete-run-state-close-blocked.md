# HO-0045: RUN-01KZ5YXM: work complete, run-state close blocked by BG0516 and BG0517

> **Date:** 2026-08-04
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZ5YXM (started 2026-08-04T08:35:53Z)
> **Outcome:** running
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 433.7 min, 6 unit(s) terminal
- **Delivered:** 6 unit(s)
- **Token forecast:** ~2,378,617 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (6)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [US0487](../../sdlc-studio/stories/US0487-a-sprint-charter-is-a-first-class-artefact.md) | story | Done | 3/3 AC(s) verified |
| [US0488](../../sdlc-studio/stories/US0488-sprint-next-materialises-the-head-charter-against-the.md) | story | Done | 3/3 AC(s) verified |
| [US0489](../../sdlc-studio/stories/US0489-the-queue-is-inspectable-and-editable-show-the.md) | story | Done | 4/4 AC(s) verified |
| [US0490](../../sdlc-studio/stories/US0490-a-charter-carries-its-own-goal-review-and.md) | story | Done | 3/3 AC(s) verified |
| [US0491](../../sdlc-studio/stories/US0491-calling-a-sprint-at-a-point-is-an.md) | story | Done | 3/3 AC(s) verified |
| [US0492](../../sdlc-studio/stories/US0492-the-queue-lifecycle-is-documented-alongside-the-run.md) | story | Done | 3/3 AC(s) verified |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Generated at the run close (`handoff generate`) |
