# CR-0567: The done-gate demands a generated mutation run over the unit's Affects beside its self-reported rows

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M1WPNV delivery, 2026-09-07: BG0646 (two REJECTs r1) and BG0649 (three REJECTs r1, two r2) - every rejection was a check a seat did in minutes that the author had not: run the shipped lane on this repository, measure a number written into prose, write a mutant for a branch the fixture never reached. Analysis recorded in the run's retro.
> **Date:** 2026-09-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Every ledger row this sprint is self-reported from a hand-written runner; `mutation.py run`, which generates mutants by fault class over a surface, was never invoked. Self-reported rows measure the mutants the author thought of, and the seats found surviving mutants on branches those rows never named. The done-gate should read a generated run over the unit's Affects files (surviving mutants ruled, or the unit refused) beside the plan rows, so the evidence covers the code as written and not only the plan as imagined.

## Impact

Mutation evidence covers the delivered code's branches, so a criterion's Verify selector that never executes a new branch is found by the generator, not by a reviewer's hand-written mutant.

## Acceptance Criteria

- [ ] Given a unit with all plan rows killed and no generated run recorded, when the depth is derived, then the field says so and the transition to Fixed refuses under `review.mutation_evidence: block`; with a generated run recorded and its survivors ruled it passes - the control.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Raised |
