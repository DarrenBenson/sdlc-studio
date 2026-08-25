# BG0607: A unit's verdict is the LAST row written, so one seat's APPROVE recorded after another seat's REJECT makes a rejected unit read approved

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 2; plan rows 2; executed 2; killed 2; survived 0; not-run 0; entry point 0 of 2 criteria through the shipped CLI, 2 in-process | fp ae72f7a3576b ]] (both directions of the rule: one seat's APPROVE cannot retire another's REJECT, and a seat may retire its own. NOT covered: whether the transition gate reads the corrected roll-up for a BUG, because a bug never reaches `Done` and the two-role gate is story-and-Done only)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01M0JD1W close, 2026-08-24. Eighteen delivery verdicts recorded across three seats; three units with a recorded REJECT print APPROVE from `critic.py show`. The blocking findings behind those REJECTs were real and were repaired, which is how the masking was noticed at all.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py show` and the gates that read it take a unit's standing verdict to be the most recently recorded row. A panel is three seats, recorded one after another, so a unit REJECTed by the engineering seat and APPROVEd by the product seat reads APPROVE whenever the product row happens to be written second. The verdict then depends on the order the recorder was invoked in, not on what the panel found. Both rows are in the log and honest; the roll-up is what is wrong.

## Steps to Reproduce

1. Record a REJECT for a unit from one reviewer. 2. Record an APPROVE for the same unit from a DIFFERENT reviewer. 3. Run `critic.py show --unit <id>`: it prints APPROVE, and the REJECT is invisible to every caller reading the head row. Observed on RUN-01M0JD1W, 2026-08-24: US0671, US0675 and US0676 each carry a seat REJECT from delivery round 2 and each reads APPROVE because the product seat was recorded last. US0674 reads REJECT only because the product seat happened to be the rejecting one.

## Proposed Fix

Resolve a unit's standing verdict across the seats of the SAME round rather than by recency: any REJECT in the round stands until a repair answers it. Report the panel as its members - `US0675 REJECT (qa, engineering) / APPROVE (product)` - so a split panel is visible as a split rather than resolved silently by write order. Keep the per-row log exactly as it is; only the roll-up changes.

## Acceptance Criteria

- [ ] **AC1** Given a unit with a REJECT from one seat and an APPROVE from another, when the standing verdict is read, then it is the REJECT - a panel is several seats recorded one after another, and taking the last row written made the verdict a fact about the order the recorder was called in
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_one_seats_approve_does_not_retire_anothers_reject
- [ ] **AC2** Given a seat that REJECTED and later APPROVED the same unit, when the standing verdict is read, then it is the APPROVE - the paired control and the boundary: a seat may change its own mind, and refusing that would make every REJECT permanent and a round-two approval unrecordable
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_a_seat_may_retire_its_own_reject

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `critic.py`, return the last live row from `verdict_for` instead of an unanswered REJECT | Given a unit with a REJECT from one seat and an APPROVE from another, when the standing verdict is read, then it is the REJECT - a panel is several seats recorded one after another, and taking the last row written made the verdict a fact about the order the recorder was called in |
| AC2 | in `critic.py`, drop the same-reviewer allowance from `verdict_for`, so no later APPROVE retires a REJECT | Given a seat that REJECTED and later APPROVED the same unit, when the standing verdict is read, then it is the APPROVE - the paired control and the boundary: a seat may change its own mind, and refusing that would make every REJECT permanent and a round-two approval unrecordable |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
