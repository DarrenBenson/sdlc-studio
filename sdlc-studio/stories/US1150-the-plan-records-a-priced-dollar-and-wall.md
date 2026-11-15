# US1150: The plan records a priced, dollar and wall-clock forecast beside tokens and minutes

> **Status:** Done
> **Delivers:** CR0694
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_plan_snapshot.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_forecast_rate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_calibration.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py, changelog.d/US1150.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0306
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** the plan records a priced, dollar and wall-clock forecast beside tokens and minutes
**So that** I know what each team's delivery costs per point and can hold it to a monthly budget

## Acceptance Criteria

- **AC1:** Given a project whose velocity history holds three or more runs with a priced-per-point figure, when `sprint plan --write` opens a run, then the run's plan snapshot records a `priced_per_point` rate with its source naming the runs it was fitted from, and each unit's row carries a priced forecast of its points times that rate.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanPricedRateTests::test_plan_write_records_priced_rate_with_source
  - **Verified:** yes (2026-11-15)
- **AC2:** Given a priced forecast and a price table listing the planned model, when the plan is written, then the snapshot records a dollar forecast equal to the priced forecast times that model's input price per million, naming the table's effective date.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanDollarForecastTests::test_dollar_forecast_names_model_and_effective_date
  - **Verified:** yes (2026-11-15)
- **AC3:** Given delivered runs with a recorded elapsed span and points, when the plan is written, then it records a wall-clock forecast in minutes from points per elapsed hour, kept apart from the active-minutes forecast.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanWallClockForecastTests::test_wall_clock_forecast_is_separate_from_active_minutes
  - **Verified:** yes (2026-11-15)
- **AC4:** Given a project with no measured rate for a row, when `sprint plan` runs (preview or --write), then it prints one line per unforecast row reading 'not forecast: <reason>' and exits 0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py::PlanUnforecastRowTests::test_plan_names_each_row_it_cannot_forecast
  - **Verified:** yes (2026-11-15)

## Notes

- Serves Abena Osei's End goal 3; delivers part of CR0694 (D0476).
- AC1 must fail on: A rate stored without its source or run list; a mean where the rolling median is used; a snapshot written by a preview (no --write); unit rows still carrying only tokens and minutes.
- AC2 must fail on: A hard-coded price; the effective date missing; a model absent from the table priced as $0 instead of 'not forecast'.
- AC3 must fail on: The wall-clock forecast written into `forecast_minutes` (the active-work figure) or derived from `minutes_per_point`.
- AC4 must fail on: A bare 'not forecast' with no reason; a non-zero exit or refusal when a rate is missing; the row silently omitted from the plan output.
- Snapshot shape and writers: `scripts/lib/run_state.py:2850` `PLAN_SNAPSHOT`, :2856 `forecast_row` (tokens and minutes only), :2872 `record_plan_snapshot`, :2893 `_snapshot_added` (added units reuse the approved rates), :2913 `plan_totals`. Extend `forecast_row` with `forecast_priced`, `forecast_usd`, `forecast_span_minutes` keys; keep None for unmeasured and keep rates frozen at the first write.
- Rates are assembled in scripts/sprint.py:295 `plan_rates` `(tokens_per_point`, `minutes_per_point`) and stamped at :320 `record_plan_snapshot`, called from `cmd_plan` at :11013 only under --write. Plan text prints at sprint.py ~4525-4550 (the 'token forecast' block); add the 'not forecast: reason' lines there.
- Priced rate source: VELOCITY rows carry a parsed `priced_per_point` cell (scripts/retro.py:989); rolling-median helpers are retro.py:2492 `_row_tokens_per_point`, :2574 and :2607 `minutes_per_point`. Add a `priced_per_point(root`) and a `points_per_elapsed_hour(root`) beside `minutes_per_point` using the same `_rolling_median`. Check VELOCITY rows hold elapsed time; if not, read `duration_hours` from signed reports' goal section (sdlc-studio/reports/RPT*.json).
- Dollars: scripts/lib/prices.py load()/Price/cost() (:350, :421), table templates/model-prices.json with per-entry effective date. 'Priced' is input-equivalent tokens (cache read 0.1, cache write 1.25, output 5), so forecast dollars = priced x input price/1e6 for the planned model `(retro.work_model`). Confirm against `run_state.usd` (:1737) before choosing the multiplier.
- Existing tests that read the snapshot or rates and may need the new keys: `test_lean_plan_snapshot.py`, `test_lean_forecast_rate.py`, `test_lean_calibration.py`, `test_sprint.py` (grep 'not forecast').
- Wall-clock is elapsed time; BG0898 stands: never compare it with active minutes. Nothing may refuse or warn on a ratio.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run twelve grooming, D0476) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
