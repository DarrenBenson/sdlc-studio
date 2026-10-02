# BG0898: The report's Minutes row divides a wall-clock span by an active-work forecast

> **Status:** In Progress
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_minutes_like_for_like.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RPT0014 Estimates table; product seat, report-honesty goal review
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T11:47:35Z

## Summary

RPT0014's Estimates table reads Minutes 416.0 forecast, 575.6 actual, 1.38x: the forecast is active work minutes per point, the actual is the run's wall-clock span start to end, so waiting counts on one side only and the ratio compares unlike measures.

## Steps to Reproduce

1. A run whose wall-clock span includes waiting. 2. `sprint_report` -> Minutes ratio = span / active forecast.

## Proposed Fix

Compare like with like: measured active minutes (unit spans or agent totals) against the forecast, and show the wall-clock span as its own labelled line with no ratio.

## Acceptance Criteria

- [ ] **AC1** Given a run with a 600-minute wall-clock span and 120 measured active unit minutes against a 100-minute forecast, when the page is derived, then the Minutes ratio reads 1.2x from the measured minutes and the 600-minute span appears on its own line with no ratio. Fails on: the current code prints 6.0x
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_minutes_like_for_like.py::MinutesLikeForLikeTests::test_the_minutes_ratio_compares_measured_with_forecast
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
