# HO-0042: A close converges in one pass and its findings count: nothing is repaired inside the close, a repaired REJECT has a route back to covered, and no close gate reports a green it did not earn

> **Date:** 2026-08-03
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZ3V4D (started 2026-08-03T13:09:22Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 13 unit(s)
- **Spent:** 286.3 min, 13 unit(s) terminal
- **Delivered:** 13 unit(s)
- **Token forecast:** ~2,982,454 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (13)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0489](../../sdlc-studio/bugs/BG0489-the-commit-msg-suite-verdict-is-written-before.md) | bug | Closed | critic APPROVE (engineering-seat-boundary-r1) |
| [BG0499](../../sdlc-studio/bugs/BG0499-panel-escalation-reads-a-different-ledger-from-the.md) | bug | Closed | critic REJECT (engineering-seat-boundary-r1) |
| [BG0492](../../sdlc-studio/bugs/BG0492-the-suite-verdict-binds-to-head-rather-than.md) | bug | Closed | critic REJECT (engineering-seat-boundary-r1) |
| [BG0502](../../sdlc-studio/bugs/BG0502-a-close-sealed-by-file-and-close-tells.md) | bug | Closed | 2/2 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0616](../../sdlc-studio/stories/US0616-sprint-close-and-sprint-stop-refuse-while-the.md) | story | Done | 4/4 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0617](../../sdlc-studio/stories/US0617-the-close-owed-ledger-distinguishes-a-close-time.md) | story | Done | 4/4 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0618](../../sdlc-studio/stories/US0618-an-unavoidable-close-time-repair-is-recorded-as.md) | story | Done | 3/3 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0619](../../sdlc-studio/stories/US0619-re-running-a-completed-close-over-an-unchanged.md) | story | Done | 3/3 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0620](../../sdlc-studio/stories/US0620-a-reject-can-be-answered-by-a-recorded.md) | story | Done | 4/4 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0621](../../sdlc-studio/stories/US0621-the-coverage-predicate-distinguishes-approved-repaired-and-unreviewed.md) | story | Done | 4/4 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0622](../../sdlc-studio/stories/US0622-a-repair-closing-fewer-findings-than-the-reject.md) | story | Done | 3/3 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0623](../../sdlc-studio/stories/US0623-a-finding-closed-by-filing-is-recorded-distinctly.md) | story | Done | 3/3 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |
| [US0624](../../sdlc-studio/stories/US0624-the-close-preflight-states-the-three-coverage-counts.md) | story | Done | 3/3 AC(s) verified; critic REJECT (engineering-seat-boundary-r1) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Generated at the run close (`handoff generate`) |
