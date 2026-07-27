# HO-0031: Harden the delivery gates and finish request derivation: close the manual-AC Done bypass, stop shell-hazard false positives, and derive parent requests at close

> **Date:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYH9QB (started 2026-07-27T07:59:57Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 38 min, 3 unit(s) terminal
- **Delivered:** 3 unit(s)
- **Token forecast:** ~1,290,707 tokens - a plan-time estimate, never a gate (a script cannot observe token spend)

## Delivered (3)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0300](../../sdlc-studio/bugs/BG0300-manual-is-a-gate-bypass-token-a-story.md) | bug | Fixed | no verifier or verdict on record |
| [US0445](../../sdlc-studio/stories/US0445-close-tail-derives-parent-crs-and-rfcs-terminal.md) | story | Done | 4/4 AC(s) verified |
| [BG0301](../../sdlc-studio/bugs/BG0301-shell-hazard-fingerprint-false-positives-on-aligned-code.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Generated at the run close (`handoff generate`) |
