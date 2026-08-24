# HO-0062: A unit's own evidence is made honest: a test that never reaches the change it claims to cover is reported rather than counted as proof, and a `Verification depth` field states only what the mutation ledger supports

> **Date:** 2026-08-24
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M0JD1W (started 2026-08-21T14:53:51Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 4442.5 min, 6 unit(s) terminal
- **Delivered:** 6 unit(s)
- **Token forecast:** ~2,710,181 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (6)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [US0671](../../sdlc-studio/stories/US0671-revert-check-reverts-a-unit-s-production-files.md) | story | Done | 14/14 AC(s) verified; critic APPROVE (product seat (subagent, delivery round 2)) |
| [US0672](../../sdlc-studio/stories/US0672-revert-check-restores-the-working-tree-byte-exact.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (product seat (subagent, delivery round 2)) |
| [US0673](../../sdlc-studio/stories/US0673-revert-check-reports-a-unit-whose-affects-names.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (product seat (subagent, delivery round 2)) |
| [US0674](../../sdlc-studio/stories/US0674-revert-check-runs-as-a-gate-lane-so.md) | story | Done | 10/10 AC(s) verified; critic REJECT (product seat (subagent, delivery round 2)) |
| [US0675](../../sdlc-studio/stories/US0675-every-count-in-verification-depth-is-read-from.md) | story | Done | 5/5 AC(s) verified; critic APPROVE (product seat (subagent, delivery round 2)) |
| [US0676](../../sdlc-studio/stories/US0676-the-derived-half-of-verification-depth-is-delimited.md) | story | Done | 9/9 AC(s) verified; critic APPROVE (product seat (subagent, delivery round 2)) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Generated at the run close (`handoff generate`) |
