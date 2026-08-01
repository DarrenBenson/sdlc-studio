# HO-0039: The sprint run is a controllable object end to end: inspectable and mutable in flight, queued as charters, and closed on evidence that can fail

> **Date:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KYX375 (started 2026-07-31T22:04:33Z)
> **Outcome:** stopped
> **Goal:** plan
> **Batch source:** run-state.json

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 424.2 min, 9 unit(s) terminal
- **Delivered:** 9 unit(s)
- **Token forecast:** ~1,062,724 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (9)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0413](../../sdlc-studio/bugs/BG0413-a-suite-that-loses-90-of-its-tests.md) | bug | Fixed | no verifier or verdict on record |
| [BG0415](../../sdlc-studio/bugs/BG0415-the-gate-budget-is-over-at-457s-against.md) | bug | Fixed | no verifier or verdict on record |
| [BG0418](../../sdlc-studio/bugs/BG0418-the-close-swallows-the-retro-validator-s-own.md) | bug | Fixed | no verifier or verdict on record |
| [BG0422](../../sdlc-studio/bugs/BG0422-the-code-is-mostly-right-and-the-evidence.md) | bug | Fixed | no verifier or verdict on record |
| [BG0460](../../sdlc-studio/bugs/BG0460-the-close-dry-run-reports-a-chain-step.md) | bug | Fixed | no verifier or verdict on record |
| [BG0466](../../sdlc-studio/bugs/BG0466-a-v3-id-carries-no-ordinal-so-every.md) | bug | Fixed | no verifier or verdict on record |
| [BG0455](../../sdlc-studio/bugs/BG0455-sprint-stop-cannot-tell-an-unbuilt-unit-from.md) | bug | Fixed | no verifier or verdict on record |
| [BG0459](../../sdlc-studio/bugs/BG0459-a-wholly-unreplaced-retro-scaffold-validates-as-filled.md) | bug | Fixed | no verifier or verdict on record |
| [BG0372](../../sdlc-studio/bugs/BG0372-the-overhead-ratio-never-reaches-the-velocity-record.md) | bug | Fixed | 4/4 AC(s) verified |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Generated at the run close (`handoff generate`) |
