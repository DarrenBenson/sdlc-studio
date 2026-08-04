# HO-0043: A shipped mechanism does what its own record claims: for every unit in this batch the gap between the claim and the behaviour is closed and proven by execution - an executed mutant where the claim is a verifier, a reproduced wrong result where the claim is behaviour

> **Date:** 2026-08-04
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZ56M6 (started 2026-08-04T01:33:13Z)
> **Outcome:** goal-reached
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 401.4 min, 7 unit(s) terminal
- **Delivered:** 7 unit(s)
- **Token forecast:** ~2,226,558 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (7)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0419](../../sdlc-studio/bugs/BG0419-four-delivered-units-are-held-by-verifiers-that.md) | bug | Fixed | 5/5 AC(s) verified |
| [BG0477](../../sdlc-studio/bugs/BG0477-refine-mints-stories-nothing-can-plan-placeholder-acceptance.md) | bug | Fixed | 3/3 AC(s) verified |
| [BG0485](../../sdlc-studio/bugs/BG0485-the-goal-review-panel-maps-a-seat-s.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0494](../../sdlc-studio/bugs/BG0494-resolve-affects-tries-the-prefix-stripped-candidate-against.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0501](../../sdlc-studio/bugs/BG0501-batch-add-epic-and-batch-swap-price-stories.md) | bug | Fixed | 2/2 AC(s) verified |
| [BG0506](../../sdlc-studio/bugs/BG0506-a-repeated-single-valued-metadata-field-is-accepted.md) | bug | Fixed | 3/3 AC(s) verified |
| [US0467](../../sdlc-studio/stories/US0467-status-names-the-open-run-id-rung-sprint.md) | story | Done | 5/5 AC(s) verified |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Generated at the run close (`handoff generate`) |
