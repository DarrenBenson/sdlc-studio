# BG1277: The close's closing-review row does not credit a unit carried at the review cap whose carrying bug was fixed and approved in the same run

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run eight (RUN-01M6RZQZ) close dry-run at d9856d1b; waiver D0425
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T22:00:30Z

## Summary

At RUN-01M6RZQZ's close the closing-review checklist row named US1130 and US1133 as unresolved, because it reads each unit's latest verdict and both end on a round-2 REJECT. Their findings were carried as BG1258 and BG1274, both in the batch and both Fixed on independent APPROVEs. `sprint_report._discharged_carry` credits only an APPROVE on the carried unit itself, so the only way through was a waiver (D0425).

## Steps to Reproduce

Carry a unit at the review cap, add its carrying bug to the batch, fix it on an independent APPROVE, then run `sprint.py close --dry-run`.

## Proposed Fix

Read a carried unit as answered when its carrying bug is terminal on an independent APPROVE inside the run, in the closing-review row and in `_discharged_carry`, and pin it.

## Acceptance Criteria

- [ ] **AC1** Given a unit carried at the review cap whose carrying bug is in the batch and Fixed on an independent APPROVE inside the run, when `sprint.py close --dry-run` prints the closing-review row, then the carried unit is not named as unresolved. Fails on: the row reading only the carried unit's latest REJECT, so a waiver is the only way through.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_a_carried_unit_whose_carrying_bug_was_approved_is_answered
- [ ] **AC2** Given the same run, when the report lists its discharged carries, then the carried unit is among them once it is terminal. Fails on: `_discharged_carry` crediting only an APPROVE on the carried unit itself.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_a_carry_answered_through_its_carrying_bug_is_discharged
- [ ] **AC3** Given a carrying bug that is not terminal, or whose only APPROVE is its author's or falls outside the run, when the closing-review row is printed, then the carried unit is still named as unresolved. Fails on: any carrying bug, whatever its state, clearing the carried unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_an_unanswered_carrying_bug_leaves_the_carry_unresolved

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
