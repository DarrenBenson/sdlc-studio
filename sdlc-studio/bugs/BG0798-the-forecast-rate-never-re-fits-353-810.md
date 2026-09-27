# BG0798: The forecast rate never re-fits: 353,810 tokens per point has forecast about twice the measured spend for three sprints

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
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

- [ ] **AC1** The behaviour described is corrected: Sprints 3-5 measured 175k-363k tokens per point (VELOCITY.md RETRO0122-RETRO0125: 175,455, 362,827, 178,352, 184,233), yet every plan still forecasts...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: retro.py velocity; compare the forecast constant with the last three measured rates.
- [ ] **AC3** The proposed fix lands, pinned by a test: At close, re-fit tokens and minutes per point from the last N runs' measured rows (out-of-sample, as the file already marks them), record the drift in the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
| 2026-09-27 | sdlc | Recurrence of BG0248 (Fixed): its fix let the rate advance from per-unit actuals, which no lean run writes (BG0797), so the rate still does not move. Fix BG0797 first or re-fit from the run total |
