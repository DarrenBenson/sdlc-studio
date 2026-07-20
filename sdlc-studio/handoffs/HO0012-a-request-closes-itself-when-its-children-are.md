# HO-0012: A request closes itself when its children are all resolved, and the sweep that does it reports exactly what it did

> **Date:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KXZ7YA (started 2026-07-20T07:35:53Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock unbounded, units unbounded
- **Spent:** 14.4 min, 3 unit(s) terminal
- **Delivered:** 3 unit(s)
- **Token forecast:** ~675,000 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (3)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [US0269](../../sdlc-studio/stories/US0269-reconcile-detect-reports-a-derivable-request-as-a.md) | story | Done | 3/3 AC(s) verified |
| [US0270](../../sdlc-studio/stories/US0270-reconcile-apply-derives-the-request-terminal-through-transition.md) | story | Done | 3/3 AC(s) verified |
| [US0271](../../sdlc-studio/stories/US0271-the-derivation-refuses-what-g2-refuses-no-childless.md) | story | Done | 4/4 AC(s) verified |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

_None recorded._ Rulings made during the run live in the tranche ledger (`sdlc-studio/decisions/`); settled decisions belong in `sdlc-studio/decisions.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Generated at the run close (`handoff generate`) |
