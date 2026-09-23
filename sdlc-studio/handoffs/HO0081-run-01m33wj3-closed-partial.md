# HO-0081: RUN-01M33WJ3 closed partial

> **Date:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M33WJ3 (started 2026-09-22T06:23:44Z)
> **Outcome:** running
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Unanswered stop-ship questions

None: every batch unit is delivered, abandoned, ruled, dropped, parked or awaiting only a signature. Rulings read from RETRO0120's `## Known issues carried` for RUN-01M33WJ3.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 1483.4 min, 5 unit(s) terminal
- **Delivered:** 5 unit(s)
- **Token forecast:** ~4,773,343 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (5)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0733](../../sdlc-studio/bugs/BG0733-a-verified-line-reading-partial-or-no-is.md) | bug | Fixed | 11/11 AC(s) verified; critic APPROVE (independent-critic) |
| [BG0715](../../sdlc-studio/bugs/BG0715-the-close-attributes-every-finding-raised-outside-a.md) | bug | Fixed | 8/8 AC(s) verified; critic APPROVE (independent-critic) |
| [BG0730](../../sdlc-studio/bugs/BG0730-a-stop-ship-ruling-is-never-re-derived.md) | bug | Fixed | 6/6 AC(s) verified; critic APPROVE (independent-critic) |
| [BG0719](../../sdlc-studio/bugs/BG0719-the-report-of-record-does-not-disclose-the.md) | bug | Fixed | 12/12 AC(s) verified; critic APPROVE (independent-critic) |
| [BG0722](../../sdlc-studio/bugs/BG0722-the-unruled-lens-catches-a-request-nobody-closed.md) | bug | Fixed | 8/8 AC(s) verified; critic APPROVE (independent-critic) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Generated at the run close (`handoff generate`) |
