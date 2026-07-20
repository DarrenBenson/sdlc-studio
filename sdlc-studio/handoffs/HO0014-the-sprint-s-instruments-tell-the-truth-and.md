# HO-0014: The sprint's instruments tell the truth and its stops respect the operator: mutation and velocity records are trustworthy, and a run asks bounded, structured questions instead of stalling in prose

> **Date:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KXZQF0 (started 2026-07-20T12:25:40Z)
> **Outcome:** goal-reached
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 240 min, units 9 unit(s)
- **Spent:** 172.8 min, 9 unit(s) terminal
- **Delivered:** 9 unit(s)
- **Token forecast:** ~750,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (9)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0215](../../sdlc-studio/bugs/BG0215-a-timed-out-mutation-run-leaves-the-mutant.md) | bug | Fixed | no verifier or verdict on record |
| [BG0218](../../sdlc-studio/bugs/BG0218-the-velocity-record-omits-delivered-points-when-the.md) | bug | Fixed | no verifier or verdict on record |
| [US0277](../../sdlc-studio/stories/US0277-mutation-run-reports-its-selected-test-files-and.md) | story | Done | 2/2 AC(s) verified |
| [US0278](../../sdlc-studio/stories/US0278-warn-when-a-test-file-that-references-the.md) | story | Done | 3/3 AC(s) verified |
| [US0279](../../sdlc-studio/stories/US0279-an-interactive-close-captures-the-harness-tracked-token.md) | story | Done | 2/2 AC(s) verified |
| [US0280](../../sdlc-studio/stories/US0280-a-unit-needing-an-operator-decision-is-set.md) | story | Done | 3/3 AC(s) verified |
| [US0281](../../sdlc-studio/stories/US0281-operator-questions-are-presented-as-structured-decisions-with.md) | story | Done | 2/2 AC(s) verified |
| [US0282](../../sdlc-studio/stories/US0282-close-offers-a-bounded-file-and-close-path.md) | story | Done | 3/3 AC(s) verified |
| [US0283](../../sdlc-studio/stories/US0283-close-reports-whether-the-outstanding-set-shrinks-or.md) | story | Done | 2/2 AC(s) verified |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

_None recorded._ Rulings made during the run live in the tranche ledger (`sdlc-studio/decisions/`); settled decisions belong in `sdlc-studio/decisions.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Generated at the run close (`handoff generate`) |
