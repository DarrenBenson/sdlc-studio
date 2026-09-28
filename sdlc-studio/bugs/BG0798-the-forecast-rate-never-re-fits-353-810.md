# BG0798: The forecast rate never re-fits: 353,810 tokens per point has forecast about twice the measured spend for three sprints

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_forecast_rate.py, changelog.d/BG0798.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T07:29:14Z

## Summary

Sprints 3-5 measured 175k-363k tokens per point (VELOCITY.md RETRO0122-RETRO0125: 175,455, 362,827, 178,352, 184,233), yet every plan still forecasts `TOKENS_PER_POINT`=353810, so RPT0010 reads 0.53x. Minutes per point falls back to RETRO0028's median because no velocity row carries a model or wall time. The lean loop's calibration channel (re-fit the rates from the run archive at each close, report the drift) is not wired.

## Steps to Reproduce

retro.py velocity; compare the forecast constant with the last three measured rates.

## Proposed Fix

At close, re-fit tokens and minutes per point from the last N runs' measured rows (out-of-sample, as the file already marks them), record the drift in the report, and have the next plan read the re-fitted rate; keep an explicit operator override.

## Acceptance Criteria

- [ ] **AC1** Given VELOCITY rows whose newest three usable rows name no single model and whose older rows name the work model (this repository's shape: RETRO0123-RETRO0125 against RETRO0094, RETRO0119, RETRO0120), when the plan reads the tokens-per-point rate, then it is the median of the newest rows and the source says they name no single model. Fails on: HEAD's `_rolling_median`, which prefers the work model's rows however old (353,810 where the newest rows give 184,233)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_forecast_rate.py::ForecastRateTests::test_a_stale_model_s_rows_do_not_outrank_newer_rows
  - **Verified:** yes (2026-09-28)
- [ ] **AC2** Given `estimate.tokens_per_point` set in the project config, when the plan forecasts, then that rate is used and the forecast basis names it an operator override. Fails on: the measured rate silently replacing the operator's figure, or the override applied without saying so
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_forecast_rate.py::ForecastRateTests::test_an_operator_rate_overrides_and_is_named
  - **Verified:** yes (2026-09-28)

## Notes

- Sprint 6 engineering: the re-fit is already wired (`sprint.tokens_per_point` re-measures from VELOCITY.md on every plan). It is stuck because `retro.measured_rate` falls back to claude-opus-5's rows RETRO0094, RETRO0119 and RETRO0120 while RETRO0121-RETRO0125 record no model (measured at dee380d9). The minutes-per-point half is deferred: no row records active minutes, so `minutes_per_point` reads RETRO0028's 6.4; file it as its own bug once BG0797's agent minutes exist for three sprints (RATE_MIN_ROWS). 5 to 3 points.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
| 2026-09-27 | sdlc | Recurrence of BG0248 (Fixed): its fix let the rate advance from per-unit actuals, which no lean run writes (BG0797), so the rate still does not move. Fix BG0797 first or re-fit from the run total |
| 2026-09-27 | sdlc-studio v6 planning | Re-scoped for Sprint 6: the re-fit exists and is starved by the model filter; a recency rule and the operator override; minutes deferred until BG0797 has three sprints |
