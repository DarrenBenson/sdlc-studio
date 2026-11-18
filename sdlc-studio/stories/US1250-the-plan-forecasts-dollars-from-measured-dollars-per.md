# US1250: The plan forecasts dollars from measured dollars per point, naming its runs, with a stated fallback

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0703
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_dollar_rate_fit.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py
> **Epic:** EP0344
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The plan forecasts dollars from measured dollars per point, naming its runs, with a stated fallback
**So that** CR0703 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The plan's dollar forecast is points times the measured dollars per point

- **Given** a project whose last five priced runs each record their points and a dollar figure
- **When** `sprint.py plan --write` forecasts a batch
- **Then** the dollar forecast equals the batch's points times the median dollars per point of those five runs, and the plan names the runs the rate was fitted from. Fails on: the forecast still computed as priced tokens times the model's input price when measured runs exist, or a fitted figure that names no runs
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanDollarForecastTests::test_dollar_forecast_is_fitted_from_measured_dollars_per_point

### AC2: Fewer than three dollar figures fall back, and the plan says so

- **Given** a project where only two runs carry a dollar figure
- **When** the same plan is written
- **Then** the dollar forecast is the priced forecast times the planned model's input price, and the plan says it fell back because fewer than three runs carry a dollar figure. Fails on: a rate fitted from two runs, or a fallback that reads as a fitted figure
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanDollarForecastTests::test_fewer_than_three_dollar_runs_fall_back_and_say_so

### AC3: The rate is the median of the most recent five runs that carry dollars

- **Given** seven closed runs, one without a dollar figure and one recent run costing ten times the rest
- **When** the dollar rate is fitted
- **Then** it is the median over the five most recent runs that carry both points and dollars, it skips the run without a figure, the outlier does not move it as it would a mean, and the result lists the run ids used. Fails on: a mean, a fit over every run on record, or a run with no dollar figure counted as zero
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_dollar_rate_fit.py::DollarRateFitTests::test_the_rate_is_the_median_of_the_last_five_dollar_runs

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
