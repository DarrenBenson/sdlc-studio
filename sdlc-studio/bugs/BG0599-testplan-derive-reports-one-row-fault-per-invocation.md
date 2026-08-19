# BG0599: testplan derive reports ONE row fault per invocation while computing all four, so authoring N mutants costs N round trips

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M0CT8P, 2026-08-19: 22 invocations to clear 33 rows, counted while authoring the batch's own test plans.
> **Created:** 2026-08-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`testplan_row_faults` computes all four row rules and RETURNS THEM AS A LIST - its own docstring says 'named rather than counted' precisely so each limb is distinguishable. Its caller in `testplan_derive` refuses on the first offending row and prints that row's faults alone, so a plan whose rows carry six faults between them takes six invocations to clear. The information to print them all is already computed and thrown away. A second, smaller gap rides along: `_EDIT_VERBS` holds `revert` but not `restore`, `disable` but not `keep`, and 61 verbs in total - the enumerated list that BG0534 and BG0563 already closed once for this same field.

## Steps to Reproduce

Measured 2026-08-19 while authoring the RUN-01M0CT8P test plans: 33 rows across six units took 22 invocations of `verify_ac.py testplan derive` before the batch derived clean, one refusal at a time. Every refusal was CORRECT - a missing edit verb, a mutant naming no path from the unit's Affects, a mutant over the 60% restatement ceiling - so this is not a false-positive report. The faults were then read in one pass by importing `testplan_row_faults` and running it over every row directly, which is the hand-rolling the toolchain runbook exists to prevent, and it took one command. `_EDIT_VERBS` was read at `verify_ac.py`:2351: `restore` is absent while `revert` is present, so 'restore the branch this fix removed' - the natural phrasing for a regression mutant - is refused.

## Proposed Fix

Report every offending row and every fault on it in ONE refusal, as the function already computes them: collect across rows rather than returning at the first. Exit code is unchanged; only the message grows. For the verb list, the durable repair is the one BG0534 and BG0563 reached for this same field - judge the phrase rather than match a literal - but adding `restore` is the honest interim, and it should be recorded as an interim rather than as a fix.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `testplan_row_faults` computes all four row rules and RETURNS THEM AS A LIST - its own docstring says 'named rather than counted' precisely so each limb is...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Measured 2026-08-19 while authoring the RUN-01M0CT8P test plans: 33 rows across six units took 22 invocations of `verify_ac.py testplan derive` before the...
- [ ] **AC3** The proposed fix lands, pinned by a test: Report every offending row and every fault on it in ONE refusal, as the function already computes them: collect across rows rather than returning at the first.

## Impact

This is the round-trip cost EP0210's contract reporter exists to remove, and it was paid while planning the sprint that was to build it. Each round trip is a full CLI invocation over the artefact, and the cost falls on the ONE activity the test-plan gate makes compulsory for every unit created after 2026-08-01 - so it scales with the backlog rather than with the defect. It also trains the reader to bypass the shipped command and call the library directly, which is how a lane stops being exercised at all.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Filed |
