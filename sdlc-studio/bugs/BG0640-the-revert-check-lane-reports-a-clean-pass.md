# BG0640: the revert-check lane reports a clean pass when it examined nothing, so an absence reads as a result

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Created:** 2026-09-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

With nothing refused and nothing crashed, the lane returns `blocking: False` with the detail `0 unit(s) examined, none stayed green without its change`. The sentence is literally true and reads as a clean bill: `none stayed green` is vacuously satisfied over an empty set, and a reader skimming a gate page meets a reassuring clause about a run that measured nothing. The CRASHED case was repaired - it now leads with the failure, on the stated reasoning that a reader should not meet the reassuring half of a sentence first - and the zero-examined case was left with exactly the shape that argument condemns.

## Steps to Reproduce

1. Run the gate on a tree where the lane examines no unit and none crashes.
2. The lane reports `0 unit(s) examined, none stayed green without its change` and does not hold.
3. Compare the crashed branch immediately above it, which leads with `N unit(s) could not be examined at all` for the opposite reason.

## Proposed Fix

Say what happened rather than what did not. When `examined` is zero, the detail should lead with the absence - `no unit was examined, so this lane measured nothing` - and never carry a clause asserting a property of the empty set. Whether zero-examined should HOLD is a separate question and probably no, since the lane is advisory; what must stop is an absence rendering as a result. The crashed branch is the model, and its comment already contains the argument.

## Acceptance Criteria

- [ ] **AC1** Given a lane run that examined zero units with none crashed, when the detail is rendered, then it leads with the absence and carries no clause asserting a property of the examined set
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckReportingTests::test_zero_examined_leads_with_the_absence
- [ ] **AC2** Given a run that examined at least one unit, when the detail is rendered, then it reports the count and the outcome as it does today - the control, without which reporting an absence unconditionally satisfies the row above
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckReportingTests::test_a_run_that_examined_units_reports_as_before

## Impact

This lane exists to catch a test that passes without the change it claims to cover. A run that examined nothing is the one case where it has learnt nothing at all, and it is the case that currently reads best on the page. It is the same class as `_ck_known_issues` failing open, filed this run as BG0638 - an absence and an answer rendering identically.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-03 | sdlc-studio | Filed |
