# HO-0019: This project can plan and judge a sprint on its own recent measured evidence, and every guard reaches the code it claims to cover

> **Date:** 2026-07-21
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KY321Q (started 2026-07-21T19:28:24Z)
> **Outcome:** stopped
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 240 min, units 8 unit(s)
- **Spent:** 113.5 min, 7 unit(s) terminal
- **Delivered:** 7 unit(s)
- **Token forecast:** ~400,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (7)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0244](../../sdlc-studio/bugs/BG0244-the-velocity-row-records-actual-tokens-as-0.md) | bug | Fixed | no verifier or verdict on record |
| [BG0246](../../sdlc-studio/bugs/BG0246-batch-history-excludes-every-interactive-sprint-so-the.md) | bug | Fixed | no verifier or verdict on record |
| [BG0242](../../sdlc-studio/bugs/BG0242-35-bare-subprocess-git-calls-in-8-test.md) | bug | Fixed | no verifier or verdict on record |
| [BG0245](../../sdlc-studio/bugs/BG0245-the-mutation-ledger-can-only-be-populated-by.md) | bug | Fixed | no verifier or verdict on record |
| [BG0240](../../sdlc-studio/bugs/BG0240-lessons-py-summary-out-and-loop-guard-py.md) | bug | Fixed | no verifier or verdict on record |
| [BG0241](../../sdlc-studio/bugs/BG0241-a-test-spec-with-no-ac-coverage-matrix.md) | bug | Fixed | no verifier or verdict on record |
| [BG0243](../../sdlc-studio/bugs/BG0243-run-attributed-tokens-reads-whatever-run-is-open.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Generated at the run close (`handoff generate`) |
