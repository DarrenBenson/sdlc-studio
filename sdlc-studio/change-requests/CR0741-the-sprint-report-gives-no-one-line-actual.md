# CR-0741: The sprint report gives no one-line actual cost, and its Estimates table puts the forecast before the actual, so a reader quotes the forecast as the run's cost

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Enhancement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** sdlc-studio/reports/RPT0035-sprint-report-run-01m7nty5.md lines 24-28; LATEST.md as committed at 712831ec quoted $172.05 and $3.37; corrected 2026-11-18.
> **Date:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T13:47:00Z

## Summary

RPT0035's cost lives only in the Estimates table, whose columns run Measure, Forecast, Actual. The forecast is the plan's points times the median rate of the last five runs, so the dollars-per-point forecast reads $3.37 run after run (RPT0034 and RPT0035 both). Run sixteen's orchestrator read the first number as the cost and told the operator, LATEST.md and its memory that the run cost $172.05 ($3.37 a point) and was dearer than run fifteen, when the Actual column says $102.01 ($2.00 a point), cheaper than run fifteen's $2.08. The page the operator signs should state what the run cost in one line before any forecast.

## Impact

The cost per point is the operator's top measure; a misread headline sends the wrong message about whether a run got dearer, and the misreading was repeated in three places before anyone checked the column.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

Put a Cost line under the verdict that states the actual priced tokens, dollars and dollars per point with the previous signed run's figures beside them, and order the Estimates table Actual then Forecast (or label the forecast column as a forecast from the plan's rate).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Raised |
