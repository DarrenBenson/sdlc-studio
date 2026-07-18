# HO-0008: Evidence earns the green: a verifier that ran nothing, a selector that cannot fail and a match made by coincidence all stop counting as proof, and the close records what it actually delivered

> **Date:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KXVD74 (started 2026-07-18T20:05:16Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 240 min, units 10 unit(s)
- **Spent:** 228.7 min, 10 unit(s) terminal
- **Delivered:** 10 unit(s)
- **Token forecast:** ~600,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (10)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0191](../../sdlc-studio/bugs/BG0191-handoff-is-generated-before-the-apply-signoff-cascade.md) | bug | Fixed | no verifier or verdict on record |
| [BG0193](../../sdlc-studio/bugs/BG0193-a-verify-line-whose-test-filter-matches-nothing.md) | bug | Fixed | no verifier or verdict on record |
| [BG0195](../../sdlc-studio/bugs/BG0195-apply-signoff-tail-passes-the-dashed-retro-id.md) | bug | Fixed | no verifier or verdict on record |
| [BG0196](../../sdlc-studio/bugs/BG0196-sprint-plan-claims-the-retro-judges-its-forecast.md) | bug | Fixed | no verifier or verdict on record |
| [US0226](../../sdlc-studio/stories/US0226-rewrite-us0166-ac3-as-a-two-file-shell.md) | story | Done | 3/3 AC(s) verified |
| [US0227](../../sdlc-studio/stories/US0227-split-non-discriminating-per-ac-selectors-so-each.md) | story | Done | 4/4 AC(s) verified |
| [US0228](../../sdlc-studio/stories/US0228-harden-the-verify-ac-grep-verb-against-a.md) | story | Done | 4/4 AC(s) verified |
| [BG0187](../../sdlc-studio/bugs/BG0187-trd-9-threat-model-still-calls-plan-py.md) | bug | Fixed | no verifier or verdict on record |
| [BG0192](../../sdlc-studio/bugs/BG0192-cross-epic-ac-is-a-bare-keyword-match.md) | bug | Fixed | no verifier or verdict on record |
| [BG0194](../../sdlc-studio/bugs/BG0194-id-search-re-has-no-trailing-digit-boundary.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

_None recorded._ Rulings made during the run live in the tranche ledger (`sdlc-studio/decisions/`); settled decisions belong in `sdlc-studio/decisions.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Generated at the run close (`handoff generate`) |
