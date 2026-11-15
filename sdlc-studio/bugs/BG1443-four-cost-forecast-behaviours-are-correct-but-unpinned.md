# BG1443: Four cost-forecast behaviours are correct but unpinned, the Minutes row's reason reads 'not forecast: not measured', and US1151's criteria name a command that never renders the rows

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_forecast_pins.py, changelog.d/BG1443.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** Run twelve (RUN-01M7E52T) reviews of US1150 and US1151: sdlc-studio/reviews/verdicts/US1150/2352e5af6137-2d625231.txt and sdlc-studio/reviews/verdicts/US1151/70aa46f88835-ab488d63.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T04:28:18Z

## Summary

Run twelve's US1150 and US1151 reviews (APPROVE, non-blocking): no test pins the five-run window of the priced rate, the Dollar cost 'no priced forecast' reason, the rule against summing only some units' forecasts, or the Dollar cost reason override (each behaves correctly when run); the Minutes row's reason 'not forecast: not measured' is too thin to act on (pre-existing); and US1151's criteria name `sprint_report.py show`, which never renders the Estimates rows (`build` and `render` do).

## Steps to Reproduce

Apply a mutant to any of the four named behaviours and run `test_plan_cost_forecast.py` and `test_estimates_cost_rows.py`: it survives.

## Proposed Fix

Pin the four behaviours; give the Minutes row a reason naming what is missing; correct US1151's criteria wording to the commands that render the rows.

## Acceptance Criteria

- [ ] **AC1** Given a mutant to the priced rate's five-run window, the Dollar cost reason, the partial-sum rule or the reason override, when the forecast tests run, then each fails. Fails on: any surviving.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_forecast_pins.py::ForecastPinTests
- [ ] **AC2** Given a run with no minutes rate, when the page renders, then the Minutes row's reason names what is missing. Fails on: 'not measured' alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_forecast_pins.py::MinutesReasonTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
