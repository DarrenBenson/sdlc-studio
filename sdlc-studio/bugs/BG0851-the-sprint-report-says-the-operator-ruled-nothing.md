# BG0851: The sprint report says the operator ruled nothing and no gate stood down when both happened

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T15:25:43Z

## Summary

Found in a consuming web project's signed run (RUN-01M3PMW3, RPT0003): the operator resolved a deferred decision with `sprint decision resolve` (force a unit to Fixed), the unit was moved with `transition --force` (a Forced-override written on the artefact), and the operator ruled a one-verdict raise of the review cap. The signed report's Rulings section reads 'the operator ruled 0 time(s)' and Waivers in force reads 'no gate stood down for this seal', because it counts only decisions-log rows and accepted waivers - not resolved sprint decisions nor Forced-override fields inside the run window. The page the operator signs understates the operator's own interventions.

## Steps to Reproduce

1. In a run, defer and resolve an operator decision with sprint decision resolve.
2. transition --force a batch unit.
3. Close and read the report's Rulings and Waivers sections.

## Proposed Fix

Count resolved sprint decisions as operator rulings, and list every batch unit carrying a Forced-override dated in the run window under Waivers in force.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Found in a consuming web project's signed run (RUN-01M3PMW3, RPT0003): the operator resolved a deferred decision with `sprint decision resolve` (force a unit...
- [ ] **AC2** The proposed fix lands, pinned by a test: Count resolved sprint decisions as operator rulings, and list every batch unit carrying a Forced-override dated in the run window under Waivers in force.

## Impact

The signed page misreports how much the human steered the run - the one thing a lights-out report must state plainly.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
