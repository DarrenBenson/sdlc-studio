# BG0890: A carried unit discharged inside the same run is reported as dropped, so the page undercounts delivery

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_discharged_carry.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** RPT0014 (RUN-01M3VF2J) Delivered to plan section
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:49Z

## Summary

RPT0014 lists US0974, US0977, US0978, BG0839, BG0824 and US0971 as 'dropped - carried at the review cap' and counts Delivered of the plan 32 of 38, Dropped 6 (15 points), though each was discharged by its rejecting reviewer's APPROVE (BG0850) inside the run and moved to Done or Fixed. The goal verdict says 40 of 40. Points, the estimates table and the velocity row (RETRO0129: 34 units, 65 points) all omit the six.

## Steps to Reproduce

1. Carry a unit at the review cap in an open run. 2. Record the rejecting reviewer's APPROVE (discharge) and move the unit terminal. 3. sprint close -> the unit reads dropped and its points are not delivered.

## Proposed Fix

Treat a unit whose carry was discharged in the run window as delivered (outcome 'delivered - discharged after a carry'), counting its points in Delivered, Estimates and the velocity row.

## Acceptance Criteria

- [ ] **AC1** Given a run whose batch unit was carried at the cap and then discharged by its rejecting reviewer's APPROVE and moved terminal inside the window, when `sprint_report` derives the page, then the unit's outcome reads delivered (after a discharged carry), its points count in Delivered of the plan and the Estimates points row, and Dropped excludes it. Fails on: the current code reads it dropped - carried at the review cap
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_discharged_carry.py::DischargedCarryTests::test_a_discharged_carry_counts_as_delivered
- [ ] **AC2** Given the same run, when the close records its VELOCITY.md row, then the row's delivered units and points include the discharged unit. Fails on: the current code's row omits it (RETRO0129 read 34 units, 65 points for a 40-unit run)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_discharged_carry.py::DischargedCarryTests::test_the_velocity_row_counts_a_discharged_carry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
| 2026-10-02 | qa seat (goal review) | AC2 added: the control beside AC1, so the goal cannot go green on a fixture |
