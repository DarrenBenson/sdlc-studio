# BG0375: The lane_contract refusal governing 475 units is asserted by no test, so a silent revert reddens nothing

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_b62b2ed2

## Summary

The repair that made `lane_contract` refuse a unit whose acceptance criteria the runner cannot read is correct in behaviour and pinned by nothing. An independent reviewer replaced the refusal condition with a constant false and ran the full scripts suite: 4,860 tests passed, identical to the figure the repair's own commit message quotes. The behaviour change governs 475 live units and can be reverted silently. This is precisely the rule US0505 shipped in this same batch - a repair that changes behaviour carries a test asserting that behaviour, so a later silent revert reddens the suite - violated by the repair made during that batch's own review.

## Steps to Reproduce

Independent re-review of 343da768. Neuter the refusal at sprint.py so the branch cannot be taken, then run the scripts suite: it stays entirely green. By contrast the trust-boundary repair in the same commit carried a differential test and killed both mutations aimed at it.

## Proposed Fix

Add a lane-contract test pair: a unit whose criteria are checkbox items - the real shape 475 units carry - asserting the contract refuses and that the refusal names the missing heading shape; and a companion unit with a proper criteria heading asserting it still returns its blocks. Both written so that reverting the refusal reddens them.

## Acceptance Criteria

### AC1: neutering the lane contract refusal reddens the suite

- **Given** the refusal that stops a unit dispatching with a contract the runner cannot read
- **When** its condition is replaced with a constant false
- **Then** the suite goes red rather than staying green, so a silent revert cannot pass
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneContractTests::test_criteria_the_runner_cannot_parse_are_refused_not_dispatched_empty
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2) | Filed |
| 2026-07-28 | Claude Opus 5 | Fixed: two LaneContractTests cases pin the refusal; neutering it to `if False:` now reddens both, where it previously left all 4,860 tests green. |
