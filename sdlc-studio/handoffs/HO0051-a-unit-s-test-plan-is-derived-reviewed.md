# HO-0051: A unit's test plan is derived, reviewed and executed before its code, and the run reports what that cost against what code review costs

> **Date:** 2026-08-06
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZBBZ0 (started 2026-08-06T11:03:33Z)
> **Outcome:** stopped
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 320.7 min, 7 unit(s) terminal
- **Delivered:** 7 unit(s)
- **Token forecast:** ~2,634,616 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (7)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0527](../../sdlc-studio/bugs/BG0527-the-one-run-slot-gate-reads-a-run.md) | bug | Fixed | 6/6 AC(s) verified; critic APPROVE (engineering) |
| [US0629](../../sdlc-studio/stories/US0629-a-test-plan-is-derived-from-the-unit.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (engineering) |
| [US0631](../../sdlc-studio/stories/US0631-the-test-plan-is-reviewed-by-an-independent.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (qa) |
| [US0630](../../sdlc-studio/stories/US0630-a-unit-reaching-delivery-without-a-reviewed-test.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (qa) |
| [US0632](../../sdlc-studio/stories/US0632-at-delivery-each-planned-mutant-is-executed-against.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (qa) |
| [US0633](../../sdlc-studio/stories/US0633-a-criterion-whose-mutant-cannot-be-named-is.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (engineering) |
| [US0634](../../sdlc-studio/stories/US0634-the-cost-is-measured-over-one-run-and.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (engineering) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Generated at the run close (`handoff generate`) |
