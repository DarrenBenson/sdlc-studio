# BG1008: A waiver recorded before the run can answer a checklist row while the page's Waivers in force section says no gate stood down

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_waivers_in_force_used.py, changelog.d/BG1008.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** Code path: sprint_report.py `_resolve_item` (no date bound) against `_waivers_in_force` (window-bounded). Live read: the RETRO0133 checklist at d7640ff3. Found by the G5 drafter.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T08:20:00Z

## Summary

`_resolve_item` (`sprint_report.py)` answers an outstanding checklist row with any accepted waiver for that item, whatever its date (`_waiver_for`), while `_waivers_in_force` lists only accepted waivers dated inside the run's window, a lower bound chosen so the section does not list 67 discharged one-shot waivers. So a standing waiver recorded in an earlier month answers a row on this run, the row reads `[WAIVED] ... (waived by D0090)`, and the section a signer reads to see which gates stood down says `no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window`. RPT0002's history is why that section exists. Found by the G5 breakdown of CR0614 (D0355).

## Steps to Reproduce

`sprint_report.py checklist --id RETRO0133` at d7640ff3 shows `[WAIVED] Sprint Goal stated and seat-reviewed BEFORE the plan: no goal (waived by D0090)` and `[WAIVED] Known issues carried ... (waived by D0215)`, both waivers recorded months before the run (read in a clone without that run's record, where the rows fall to the waivers). RPT0019's Waivers in force section reads `no gate stood down for this seal`. The divergence is the two functions' differing date rules.

## Proposed Fix

List in Waivers in force every waiver that answered a row or gate on this run, whatever its date, beside those recorded in the window; or make a row honour only a waiver in force for the run (CR0614's run scope). Decide with CR0614.

## Acceptance Criteria

- [ ] **AC1** A page whose checklist row was answered by a waiver dated before the run names that waiver in Waivers in force, and the section never says no gate stood down while a row it lists is WAIVED
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_waivers_in_force_used.py::WaiversInForceTests::test_a_waiver_that_answered_a_row_is_listed_whatever_its_date

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
