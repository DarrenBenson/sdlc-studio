# HO-0016: The freshness spine certifies a Done story truthfully in both directions: a Verified AC goes stale when the test it names disappears, ac_fingerprint is pinned by its own test, and a repo-wide-invariant AC no longer un-Dones a shipped story as the repo grows

> **Date:** 2026-07-21
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KY0VNV (started 2026-07-20T22:50:16Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 240 min, units 8 unit(s)
- **Spent:** 35.5 min, 3 unit(s) terminal
- **Delivered:** 3 unit(s)
- **Token forecast:** ~200,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (3)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0231](../../sdlc-studio/bugs/BG0231-a-done-story-stays-green-after-the-test.md) | bug | Fixed | no verifier or verdict on record |
| [BG0232](../../sdlc-studio/bugs/BG0232-ac-fingerprint-has-no-test-of-its-own.md) | bug | Fixed | no verifier or verdict on record |
| [BG0234](../../sdlc-studio/bugs/BG0234-a-story-ac-asserting-a-repo-wide-invariant.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

_None recorded._ Rulings made during the run live in the tranche ledger (`sdlc-studio/decisions/`); settled decisions belong in `sdlc-studio/decisions.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Generated at the run close (`handoff generate`) |
