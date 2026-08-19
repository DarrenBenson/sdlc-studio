# HO-0060: A design run that did its work can be closed, committed and counted honestly - no wall a command cannot clear, and no count that overstates what blocks

> **Date:** 2026-08-19
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M0ATVZ (started 2026-08-18T16:07:28Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 1113.4 min, 4 unit(s) terminal
- **Delivered:** 4 unit(s)
- **Token forecast:** ~1,532,288 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (4)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0585](../../sdlc-studio/bugs/BG0585-the-derived-only-grooming-detector-is-defeated-by.md) | bug | Fixed | 6/6 AC(s) verified; critic APPROVE (qa seat (subagent, repair round)) |
| [BG0584](../../sdlc-studio/bugs/BG0584-the-tick-verification-checklist-row-is-rung-blind.md) | bug | Fixed | 6/6 AC(s) verified; critic APPROVE (qa seat (subagent, repair round)) |
| [BG0589](../../sdlc-studio/bugs/BG0589-the-close-pre-flight-counts-advisory-rows-as.md) | bug | Fixed | 4/4 AC(s) verified; critic APPROVE (qa seat (subagent)) |
| [BG0590](../../sdlc-studio/bugs/BG0590-sprint-close-appends-a-handoff-bullet-that-fails.md) | bug | Fixed | 11/11 AC(s) verified; critic APPROVE (qa seat (subagent, repair round)) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Generated at the run close (`handoff generate`) |
