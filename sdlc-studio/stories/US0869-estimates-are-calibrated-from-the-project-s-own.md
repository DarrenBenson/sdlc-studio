# US0869: Estimates are calibrated from the project's own runs, not a seed constant

> **Status:** In Progress
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_calibration.py
> **Epic:** EP0260
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator reading a sprint forecast
**I want** the token and minute rates calibrated from this project's own recent runs
**So that** forecasts improve run by run instead of resting on a constant that has never been re-fitted

## Acceptance Criteria

- **AC1:** Given a velocity history whose rows span several models plus rows with no recorded model, when the token rate is measured for model M, then it is the median tokens per point of the most recent 5 usable rows for M, rows with no model or several models are skipped rather than refusing the whole history, and the source reads measured and names the rows used
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_calibration.py::TokenRateTests::test_a_mixed_model_history_yields_the_current_models_rolling_median
- **AC2:** Given fewer than 3 usable rows for M, when the rate is measured, then it falls back to the most recent 5 usable single-model rows of any model with a source saying so, and only with no usable row at all returns the seed with source seed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_calibration.py::TokenRateTests::test_a_thin_history_falls_back_before_the_seed
- **AC3:** Given this repository's own sdlc-studio/retros/VELOCITY.md, when `sprint.tokens_per_point` is called, then its source is not seed - the corpus check that planning uses a live rate
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_calibration.py::TokenRateTests::test_this_repository_plans_on_a_measured_rate
- **AC4:** Given velocity rows that record active minutes, when the minute rate is measured, then it is the rolling median minutes per point by the same rule, and with no minutes recorded it returns not measured rather than a number
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_calibration.py::MinuteRateTests::test_minutes_per_point_is_measured_or_says_not_measured

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
