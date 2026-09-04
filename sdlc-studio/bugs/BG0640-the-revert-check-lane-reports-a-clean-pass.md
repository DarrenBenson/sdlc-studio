# BG0640: the revert-check lane reports a clean pass when it examined nothing, so an absence reads as a result

> **Status:** Fixed
> **Verification depth:** functional
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

Plan review round 1 (2026-09-04): all three seats approved and all three named the crashed branch's `0 examined and clean` as the same shape one line away; AC3 pins it. AC1's fixture must reach `examined == 0` through a non-empty batch, because the empty-batch path already returns `N/A` and would pass on today's code.

Plan review round 2 (2026-09-04): the QA seat found the existing `test_a_reported_unit_is_not_counted_as_examined` drives AC1's exact fixture and asserts today's phrase, so the fix reddens it; AC1 names it and its re-authoring. AC3 asserts order, and AC1 requires the test's own root.

## Acceptance Criteria

- [ ] **AC1** Given a NON-EMPTY batch under the test's OWN fixture root (never the repository's `.local`, which `_record_revert_yield` writes to) in which every unit's `revert_check` answers `reported` or `error` and none crashed, when the detail is rendered, then it leads with `no unit was examined` and says why WITH NUMBERS - the fixture batch holds one unit, so two runs assert `1 reported, 0 in error` and `0 reported, 1 in error` - and carries neither `stayed green` nor `examined and clean` - asserted by prefix and by two absences, because `examined` appears in today's string too. The existing `RevertCheckLaneTests::test_a_reported_unit_is_not_counted_as_examined` drives exactly this fixture and asserts today's `0 unit(s) examined` phrase, so the fix REDDENS it: it is re-authored under its own name in the same commit to assert the new lead AND keep its yield-pair claim (`count == 0` and the recorder called with zero examined). `test_a_unit_the_lane_cannot_examine_is_not_reported_as_a_clean_pass` asserts the crash text and survives
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckReportingTests::test_zero_examined_leads_with_the_absence
  - **Verified:** yes (2026-09-04)
- [ ] **AC2** Given a run that examined at least one unit, when the detail is rendered, then it reports the count and the outcome as it does today - the control, without which reporting an absence unconditionally satisfies the row above
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckReportingTests::test_a_run_that_examined_units_reports_as_before
  - **Verified:** yes (2026-09-04)
- [ ] **AC3** Given zero examined AND at least one crash, when the detail is rendered, then the crash count comes FIRST and `no unit was examined` follows it - asserted on ORDER (`index("could not be examined") < index("no unit was examined")` on the detail), with `examined and clean` asserted absent in any form; the sibling branch (gate.py `; {examined} examined and clean`) carries the same property of the empty set, and a fix that repairs one branch and leaves its sibling is what this repository's last two review rounds found
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckReportingTests::test_zero_examined_with_crashes_never_reads_clean
  - **Verified:** yes (2026-09-04)

## Impact

This lane exists to catch a test that passes without the change it claims to cover. A run that examined nothing is the one case where it has learnt nothing at all, and it is the case that currently reads best on the page. It is the same class as `_ck_known_issues` failing open, filed this run as BG0638 - an absence and an answer rendering identically.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/gate.py` `_revert_check`, delete the zero-examined branch so `examined == 0` falls through to `f"{examined} unit(s) examined, none stayed green without its change"` - today's code | Given a NON-EMPTY batch under the test's OWN fixture root (never the repository's `.local`, which `_record_revert_yield` writes to) in which every unit's `revert_check` answers `reported` or `error` and none crashed, when the detail is rendered, then it leads with `no unit was examined` and says why WITH NUMBERS - the fixture batch holds one unit, so two runs assert `1 reported, 0 in error` and `0 reported, 1 in error` - and carries neither `stayed green` nor `examined and clean` - asserted by prefix and by two absences, because `examined` appears in today's string too. The existing `RevertCheckLaneTests::test_a_reported_unit_is_not_counted_as_examined` drives exactly this fixture and asserts today's `0 unit(s) examined` phrase, so the fix REDDENS it: it is re-authored under its own name in the same commit to assert the new lead AND keep its yield-pair claim (`count == 0` and the recorder called with zero examined). `test_a_unit_the_lane_cannot_examine_is_not_reported_as_a_clean_pass` asserts the crash text and survives |
| AC1 | in `.claude/skills/sdlc-studio/scripts/gate.py` `_revert_check`, render the absence without the reported and error counts | Given a NON-EMPTY batch under the test's OWN fixture root (never the repository's `.local`, which `_record_revert_yield` writes to) in which every unit's `revert_check` answers `reported` or `error` and none crashed, when the detail is rendered, then it leads with `no unit was examined` and says why WITH NUMBERS - the fixture batch holds one unit, so two runs assert `1 reported, 0 in error` and `0 reported, 1 in error` - and carries neither `stayed green` nor `examined and clean` - asserted by prefix and by two absences, because `examined` appears in today's string too. The existing `RevertCheckLaneTests::test_a_reported_unit_is_not_counted_as_examined` drives exactly this fixture and asserts today's `0 unit(s) examined` phrase, so the fix REDDENS it: it is re-authored under its own name in the same commit to assert the new lead AND keep its yield-pair claim (`count == 0` and the recorder called with zero examined). `test_a_unit_the_lane_cannot_examine_is_not_reported_as_a_clean_pass` asserts the crash text and survives |
| AC2 | in `.claude/skills/sdlc-studio/scripts/gate.py` `_revert_check`, render the absence sentence unconditionally, dropping the examined count and outcome for `examined > 0` | Given a run that examined at least one unit, when the detail is rendered, then it reports the count and the outcome as it does today - the control, without which reporting an absence unconditionally satisfies the row above |
| AC3 | in `.claude/skills/sdlc-studio/scripts/gate.py` `_revert_check`, keep `; {examined} examined and clean` on the crashed branch | Given zero examined AND at least one crash, when the detail is rendered, then the crash count comes FIRST and `no unit was examined` follows it - asserted on ORDER (`index("could not be examined") < index("no unit was examined")` on the detail), with `examined and clean` asserted absent in any form; the sibling branch (gate.py `; {examined} examined and clean`) carries the same property of the empty set, and a fix that repairs one branch and leaves its sibling is what this repository's last two review rounds found |
| AC3 | in `.claude/skills/sdlc-studio/scripts/gate.py` `_revert_check`, append the crash count after the absence sentence instead of leading with it | Given zero examined AND at least one crash, when the detail is rendered, then the crash count comes FIRST and `no unit was examined` follows it - asserted on ORDER (`index("could not be examined") < index("no unit was examined")` on the detail), with `examined and clean` asserted absent in any form; the sibling branch (gate.py `; {examined} examined and clean`) carries the same property of the empty set, and a fix that repairs one branch and leaves its sibling is what this repository's last two review rounds found |
| AC3 | in `.claude/skills/sdlc-studio/scripts/gate.py` `_revert_check`, render the absence on the crashed branch unconditionally, even when units were examined - the control the review asked for | Given zero examined AND at least one crash, when the detail is rendered, then the crash count comes FIRST and `no unit was examined` follows it - asserted on ORDER (`index("could not be examined") < index("no unit was examined")` on the detail), with `examined and clean` asserted absent in any form; the sibling branch (gate.py `; {examined} examined and clean`) carries the same property of the empty set, and a fix that repairs one branch and leaves its sibling is what this repository's last two review rounds found |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-03 | sdlc-studio | Filed |
| 2026-09-04 | sdlc-studio | Plan review round 1 (three seats): criteria and test plan re-authored to the findings; see the Proposed Fix note dated 2026-09-04 |
| 2026-09-04 | sdlc-studio | Plan review round 2 (three seats): fixtures that could not reach their branch repaired; see the Proposed Fix note |
| 2026-09-04 | sdlc-studio | Plan review round 3 (three seats): delivery notes folded into the criteria; BG0642 AC3 gains the wrong-acknowledgement step |
