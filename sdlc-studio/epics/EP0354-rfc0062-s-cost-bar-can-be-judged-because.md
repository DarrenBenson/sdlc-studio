# EP0354: RFC0062's cost bar can be judged because its baseline, its re-measure and its owed decision each have a unit

> **Status:** Draft
> **Derived Point Total:** 12
> **Parent:** CR0715
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0715. Delivers the work CR0715 requested.

## Story Breakdown

- [ ] [US1266: The Phase 2 baseline runs the benchmark at the pinned skill commit in each installed harness and commits the result](../stories/US1266-the-phase-2-baseline-runs-the-benchmark-at.md)
- [ ] [US1267: The Phase 5 re-measure publishes cost per point by harness and states plainly whether the 40 per cent bar was met](../stories/US1267-the-phase-5-re-measure-publishes-cost-per.md)
- [ ] [US1268: A decision amends D0416 and names the owner of the models and effort review, and the review page lists what RFC0062 still owes](../stories/US1268-a-decision-amends-d0416-and-names-the-owner.md)

## Acceptance Criteria (Epic Level)

- [ ] A sized unit exists for the Phase 2 baseline at 5057f7ef in each installed CLI harness, and its result is committed under docs/benchmarks
- [ ] A sized unit exists for the Phase 5 re-measure against the bar, publishing cost per point by harness and stating plainly whether the 40 per cent bar was met
- [ ] The models and effort review area is owned by a named unit, or a recorded decision drops it with its reason
- [ ] A decision amends D0416, stating which release now carries CR0670, CR0672 and the Phase 2 benchmark, and RFC0062's Decomposed-into list and the owed line of LATEST.md name the new units

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
