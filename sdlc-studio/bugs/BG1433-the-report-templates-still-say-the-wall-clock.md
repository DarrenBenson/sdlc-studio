# BG1433: The report templates still say the wall-clock span has no ratio, which is wrong on a page filed under the cost-forecast mark

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/scripts/tests/test_report_template_forecast_text.py, changelog.d/BGXXXX.md
> **Evidence:** Run twelve (RUN-01M7E52T) US1151 builder hand-back
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T01:16:10Z

## Summary

US1151 gave the Estimates table's Wall-clock span row a forecast and ratio under a new `cost_forecast` envelope mark, but `templates/core/sprint-report.md` and `templates/reports/sprint-report.html` (outside its Affects) still say the span has 'no ratio', and the 'forecasts are descriptive' sentence sits in the first forecast row's basis rather than in the text above the table.

## Steps to Reproduce

Read the Estimates text in templates/core/sprint-report.md after US1151: it says the wall-clock span has no ratio.

## Proposed Fix

Say in both templates that the span has a forecast and ratio on pages carrying the cost-forecast mark, and move the descriptive-forecasts sentence to the text above the table.

## Acceptance Criteria

- [ ] **AC1** Given the two report templates, when a reader reads the Estimates text, then neither says the wall-clock span has no ratio, and the text above the table says forecasts are descriptive. Fails on: either template still saying 'no ratio' for the span.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_template_forecast_text.py::TemplateForecastTextTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
