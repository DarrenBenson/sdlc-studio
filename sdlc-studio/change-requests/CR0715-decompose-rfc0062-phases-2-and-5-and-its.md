# CR-0715: Decompose RFC0062 Phases 2 and 5 and its models and effort review so its cost bar can be judged

> **Status:** In Progress
> **Decomposed-into:** EP0354
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/rfcs/RFC0062-token-efficient-delivery-a-sprint-costs-at-most.md, sdlc-studio/decisions.md, sdlc-studio/change-requests/CR0672-add-a-deterministic-sprint-py-drive-loop-that.md, sdlc-studio/reviews/LATEST.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, rfc lens, survived 3 of 3 refute votes; observed at sdlc-studio/rfcs/RFC0062-token-efficient-delivery-a-sprint-costs-at-most.md ## Phased Plan items 2 and 5; ## Phase 3 Result last line; decisions.md D0411, D0416, D0474
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:16Z

## Summary

RFC0062 is Accepted, and its bar includes the benchmark's skill arm costing at least 40 per cent less per fixture than the skill pinned at commit 5057f7ef in each CLI harness measured. Phase 2, which runs that baseline, and Phase 5, which re-measures against the bar and publishes cost per point by harness, have no CR, story or bug: the nineteen decomposed CRs cover only Phase 1 tooling and the Phase 3 findings. The seventh review area, models and effort, is declared not covered until the Phase 2 benchmark with no unit to pick it up. D0416 placed CR0670 and CR0672 in 6.4 with the Phase 2 benchmark, but v6.4.0 is released, CR0672 is still Proposed, no baseline result exists anywhere in the repository, and D0474's 6.4 plan omits both without amending D0416. The RFC therefore reads Accepted with nothing tracking the measurement that would show whether it worked.

## Impact

The operator and anyone citing RFC0062's saving. Half of the RFC's bar cannot be judged, a negative result cannot be recorded, and a decision that scheduled work for 6.4 has lapsed silently, so the backlog and the review page of record both understate what is owed.

## Acceptance Criteria

- [ ] A sized unit exists for the Phase 2 baseline at 5057f7ef in each installed CLI harness, and its result is committed under docs/benchmarks
- [ ] A sized unit exists for the Phase 5 re-measure against the bar, publishing cost per point by harness and stating plainly whether the 40 per cent bar was met
- [ ] The models and effort review area is owned by a named unit, or a recorded decision drops it with its reason
- [ ] A decision amends D0416, stating which release now carries CR0670, CR0672 and the Phase 2 benchmark, and RFC0062's Decomposed-into list and the owed line of LATEST.md name the new units

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
