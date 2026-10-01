# HO-0093: Maya signs, without a re-close, a report that checks VALID and names every operator ruling and carry

> **Date:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M3T8N1 (started 2026-09-30T23:00:50Z)
> **Outcome:** running
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Unanswered stop-ship questions

None: every batch unit is delivered, abandoned, ruled, dropped, parked or awaiting only a signature. Rulings read from RETRO0128's `## Known issues carried` for RUN-01M3T8N1.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 527.9 min, 9 unit(s) terminal
- **Delivered:** 9 unit(s)
- **Token forecast:** ~4,637,152 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (9)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0826](../../sdlc-studio/bugs/BG0826-the-scaffolded-retro-carries-neither-the-run-id.md) | bug | Fixed | 2/2 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |
| [BG0859](../../sdlc-studio/bugs/BG0859-the-close-s-status-preflight-stops-every-approved.md) | bug | Fixed | 1/1 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |
| [BG0848](../../sdlc-studio/bugs/BG0848-sprint-sign-invalidates-its-own-report-when-it.md) | bug | Fixed | 2/2 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |
| [BG0829](../../sdlc-studio/bugs/BG0829-a-unit-carried-at-the-review-cap-is.md) | bug | Fixed | 2/2 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |
| [BG0850](../../sdlc-studio/bugs/BG0850-a-carried-unit-s-discharge-approval-is-refused.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |
| [BG0851](../../sdlc-studio/bugs/BG0851-the-sprint-report-says-the-operator-ruled-nothing.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |
| [BG0849](../../sdlc-studio/bugs/BG0849-a-close-dry-run-mints-a-different-graduation.md) | bug | Fixed | 2/2 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |
| [BG0862](../../sdlc-studio/bugs/BG0862-nothing-runs-the-unstubbed-close-sign-and-check.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |
| [BG0865](../../sdlc-studio/bugs/BG0865-the-signed-page-names-a-known-issue-s.md) | bug | Fixed | 3/3 AC(s) verified; critic APPROVE (qa-seat reviewer (subagent a302a39d)) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Generated at the run close (`handoff generate`) |
