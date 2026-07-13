# CR-0231: protocol v3: longitudinal and multi-team fixtures for the compounding-value story

> **Status:** Superseded
> **Target:** v4.1
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Operator observation from the v4 rerun (2026-07-10): the single-ticket fixtures cannot measure where the pipeline's value compounds - brownfield repos and long-running projects (spec drift accumulates across changes; vibe coding has no mechanism to keep intent current) and multi-team concurrency (id collisions, index races, review handoffs). Even frontier models should degrade on a SEQUENCE without enforced reconciliation, because each ticket's context depends on the previous ticket's paperwork being true. Design protocol v3 fixtures: (a) a longitudinal fixture - one workspace, 4-6 dependent tickets where ticket N's correct implementation requires the spec updates tickets 1..N-1 should have made, hidden suite run after the LAST ticket; (b) a multi-team fixture - two concurrent agents on one workspace filing artifacts and cross-reviewing. Pre-register before running, per the house discipline.

## Acceptance Criteria

- [ ] Protocol v3 pre-registration exists with the longitudinal fixture (dependent-ticket sequence, drift-sensitive hidden suite validated both ways) and the multi-team fixture (concurrent writers, collision/index/review oracles)
- [ ] Both fixtures satisfy the fairness invariant (everything needed to pass is present in the visible workspace at each step)
- [ ] The v4-rerun mandated-arm addendum result is folded into the v3 arm design (mandated engagement as a first-class arm, not a variant)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
| 2026-07-13 | Darren | Superseded: re-homed to the `sdlc-bench` repo, which now owns the protocol and fixtures under RFC0029. Protocol v3 design is that project's workstream, not an sdlc-studio v4.1 tag blocker. Refiled as a `sdlc-bench` artefact. |
