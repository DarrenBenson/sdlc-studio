# BG1555: The PRD gives three different accounts of what the sprint close runs and none matches the shipped chain

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 3 of 3 refute votes; observed at sdlc-studio/prd.md Mission (lines 67-69); Section 3 row 'Sprint report and sign' (line 324); Section 4 Core Behaviours (lines 437-440)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:48Z

## Summary

The PRD describes the sprint close in three places and the three do not agree. The Section 3 row for the sprint report lists the chain as goal verdict, retro, lessons, gate and reconcile; Section 4 lists review coverage, retro, lessons, gate and reconcile; and the Mission paragraph treats the goal verdict as a precondition, not a chain step. The difference is not cosmetic, because Section 4 says a failed chain step is a known issue carried to the report while a precondition refuses the close, so the PRD does not settle what a missing goal verdict does. The shipped chain in `sprint.py` has ten steps, and three of them (persona-memory, checklist and review-anchor) appear in neither list, so a rebuild from this blueprint would leave them out.

## Steps to Reproduce

1. Open sdlc-studio/prd.md and read the Mission paragraph at lines 67 to 69: the goal verdict is listed as a precondition of the close.
2. Read the Section 3 row named Sprint report and sign at line 324: the chain is given as goal verdict, retro, lessons, gate, reconcile.
3. Read Section 4 Core Behaviours at lines 437 to 440: the chain is given as review coverage, retro, lessons, gate, reconcile, and a failed step is a known issue, not a refusal.
4. Open .claude/skills/sdlc-studio/scripts/sprint.py and read `_CLOSE_CHAIN` at lines 6404 to 6406: ten steps, namely review-coverage, retro-validate, retro-extract, retro-accuracy, persona-memory, lessons-summary, checklist, gate, reconcile and review-anchor.
5. In the same file read the close command near line 10440: a missing sprint goal and a goal verdict given without a note are refusals raised before the chain starts.
6. Observe that the three PRD passages disagree with each other and that none names persona-memory, checklist or review-anchor.

## Proposed Fix

State the close once in the PRD and make the other two passages agree with it. Name the goal and the goal verdict as preconditions that refuse the close, and list the chain as the ten steps `_CLOSE_CHAIN` holds (grouping the three retro steps is fine if the grouping is said). Keep the rule that a failed chain step is carried to the report. Extend the PRD refresh test so it reads `_CLOSE_CHAIN` from `sprint.py` and fails when a chain step is missing from the PRD's account or when the goal verdict is described as a chain step.

## Acceptance Criteria

- [ ] **AC1** Given `_CLOSE_CHAIN` in `sprint.py`, when the test reads it and the PRD's single account of the sprint close, then every chain step is named in that account (the three retro steps may be grouped where the grouping is said), including persona-memory, checklist and review-anchor. Fails on: a shipped chain step absent from the PRD's account.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdCloseChainTests::test_every_close_chain_step_is_named
- [ ] **AC2** Given the Mission paragraph, the Sprint report and sign row and Section 4 Core Behaviours, when each is read, then the sprint goal and the goal verdict are described as preconditions that refuse the close, none lists the goal verdict as a chain step, and the rule that a failed chain step is carried to the report is kept. Fails on: any passage listing the goal verdict among the chain steps, or two passages giving different step lists.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdCloseChainTests::test_the_goal_verdict_is_a_precondition_in_all_three_passages
- [ ] **AC3** Given a copy of the PRD with one chain step's name removed from the account, when the same check runs over it, then it names the missing step. Fails on: a check that passes a PRD the chain has outgrown.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdCloseChainTests::test_a_dropped_chain_step_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
