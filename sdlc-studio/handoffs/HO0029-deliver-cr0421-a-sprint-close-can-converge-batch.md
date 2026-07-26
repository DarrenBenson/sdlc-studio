# HO-0029: Deliver CR0421: a sprint close can converge - batch mutable (drop/add), correctness batch-scoped, growing set offers the bounded exit, currency judged by the review record

> **Date:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYF92Y (started 2026-07-26T13:26:41Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 213.9 min, 4 unit(s) terminal
- **Delivered:** 4 unit(s)
- **Token forecast:** ~1,922,082 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (4)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [US0433](../../sdlc-studio/stories/US0433-sprint-batch-drop-and-add-mutate-an-open.md) | story | Done | 3/3 AC(s) verified |
| [US0434](../../sdlc-studio/stories/US0434-the-close-correctness-lanes-are-batch-scoped-or.md) | story | Done | 2/2 AC(s) verified |
| [US0435](../../sdlc-studio/stories/US0435-a-growing-outstanding-set-across-close-attempts-offers.md) | story | Done | 3/3 AC(s) verified |
| [US0436](../../sdlc-studio/stories/US0436-review-currency-is-judged-by-the-review-record.md) | story | Done | 3/3 AC(s) verified |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Generated at the run close (`handoff generate`) |
