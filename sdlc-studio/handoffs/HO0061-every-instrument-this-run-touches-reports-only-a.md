# HO-0061: Every instrument this run touches reports only a verdict its own recorded evidence supports, and refuses rather than softens when the evidence is not there

> **Date:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M0CT8P (started 2026-08-19T10:57:55Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 2873.1 min, 6 unit(s) terminal
- **Delivered:** 6 unit(s)
- **Token forecast:** ~2,020,985 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (6)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0593](../../sdlc-studio/bugs/BG0593-close-dry-run-previews-against-a-scratch-tree.md) | bug | Fixed | 6/6 AC(s) verified; critic REJECT (engineering seat (subagent, delivery round 6)) |
| [BG0598](../../sdlc-studio/bugs/BG0598-the-plan-s-built-not-closed-exclusion-reads.md) | bug | Fixed | 6/6 AC(s) verified; critic REJECT (engineering seat (subagent, delivery round 6)) |
| [BG0594](../../sdlc-studio/bugs/BG0594-the-budget-lane-watches-the-per-commit-gate.md) | bug | Fixed | 6/6 AC(s) verified; critic REJECT (engineering seat (subagent, delivery round 6)) |
| [BG0595](../../sdlc-studio/bugs/BG0595-the-commit-msg-hook-test-is-not-hermetic.md) | bug | Fixed | 5/5 AC(s) verified; critic REJECT (engineering seat (subagent, delivery round 6)) |
| [BG0596](../../sdlc-studio/bugs/BG0596-testplan-run-from-plan-keys-by-criterion-so.md) | bug | Fixed | 8/8 AC(s) verified; critic REJECT (engineering seat (subagent, delivery round 6)) |
| [BG0597](../../sdlc-studio/bugs/BG0597-testplan-derive-silently-destroys-an-authored-test-plan.md) | bug | Fixed | 5/5 AC(s) verified; critic REJECT (engineering seat (subagent, delivery round 6)) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Generated at the run close (`handoff generate`) |
