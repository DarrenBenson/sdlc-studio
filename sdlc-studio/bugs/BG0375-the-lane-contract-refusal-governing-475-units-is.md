# BG0375: The lane_contract refusal governing 475 units is asserted by no test, so a silent revert reddens nothing

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2); agent; skill v5.0.0

## Summary

The repair that made `lane_contract` refuse a unit whose acceptance criteria the runner cannot read is correct in behaviour and pinned by nothing. An independent reviewer replaced the refusal condition with a constant false and ran the full scripts suite: 4,860 tests passed, identical to the figure the repair's own commit message quotes. The behaviour change governs 475 live units and can be reverted silently. This is precisely the rule US0505 shipped in this same batch - a repair that changes behaviour carries a test asserting that behaviour, so a later silent revert reddens the suite - violated by the repair made during that batch's own review.

## Steps to Reproduce

Independent re-review of 343da768. Neuter the refusal at sprint.py so the branch cannot be taken, then run the scripts suite: it stays entirely green. By contrast the trust-boundary repair in the same commit carried a differential test and killed both mutations aimed at it.

## Proposed Fix

Add a lane-contract test pair: a unit whose criteria are checkbox items - the real shape 475 units carry - asserting the contract refuses and that the refusal names the missing heading shape; and a companion unit with a proper criteria heading asserting it still returns its blocks. Both written so that reverting the refusal reddens them.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: `steps` carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (independent re-review of 343da768, run wf_b62b2ed2) | Filed |
