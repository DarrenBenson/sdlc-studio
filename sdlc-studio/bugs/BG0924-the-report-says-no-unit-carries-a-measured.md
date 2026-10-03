# BG0924: The report says no unit carries a measured time when units carry minutes but none has a forecast

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_minutes_reason_true.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG0924.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T02:08:15Z

## Summary

Under BG0898's like-for-like Minutes rule, the actual's reason reads 'no unit carries a measured time' (`sprint_report.py` ~3668) when units do carry measured minutes but none also carries a forecast, so the page states a false reason.

## Steps to Reproduce

1. A run whose units carry measured minutes and no forecast. 2. Build the page. 3. The Minutes reason says no unit carries a measured time.

## Proposed Fix

Name the actual reason: no unit carries both a forecast and a measured time. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a run whose units carry measured minutes but no forecast, when the page is built, then the Minutes reason says no unit carries both a forecast and a measured time, and a run with no measured minutes still reads that no unit carries a measured time. Fails on: the current reason
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_minutes_reason_true.py::MinutesReasonTrueTests::test_the_reason_names_the_missing_pair

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
