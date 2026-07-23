# US0400: the forecast names the rung it prices and reads UNMEASURED where that rung has no rate

> **Status:** Draft
> **Verification depth:** functional - node-addressed tests in test_forecast_rung/test_nondone_close green; EP0151 mutation-proven (4 mutants killed across the rung label, unmeasured-rung rate, and the non-done velocity blank)
> **Delivers:** CR0407
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0151
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_forecast_rung.py

## User Story

**As a** operator planning a sprint at a rung other than the build rung
**I want** the token forecast to state which `--goal` rung it prices, and read UNMEASURED for a rung it has no measured rate for
**So that** I do not plan capacity for a design run against the build cost of the batch it only grooms

## Acceptance Criteria

### AC1: the forecast names the rung it prices

- **Given** a batch planned with `--goal design`
- **When** the token forecast is built for that batch
- **Then** the forecast record names the `design` rung it priced, so a design run is never silently presented under the build rung's number
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_forecast_rung.py::ForecastNamesItsRung::test_design_rung_forecast_labels_the_rung

### AC2: an unmeasured rung reads UNMEASURED rather than borrowing the build rate

- **Given** a `design` rung for which no per-rung rate has been measured on this project
- **When** the token forecast is built
- **Then** the rate for that rung reads UNMEASURED instead of substituting the build (`done`) rate, the same refusal the cross-model rate check already makes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_forecast_rung.py::ForecastNamesItsRung::test_unmeasured_rung_rate_reads_unmeasured

### AC3: the build rung is unaffected

- **Given** a `--goal done` batch on a project carrying a measured build rate
- **When** the token forecast is built
- **Then** it still prices the batch at the measured build rate and names the `done` rung, so the honest build case is not regressed by the rung labelling
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_forecast_rung.py::ForecastNamesItsRung::test_build_rung_still_priced_and_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
