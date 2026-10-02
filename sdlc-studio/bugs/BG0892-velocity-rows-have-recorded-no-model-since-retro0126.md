# BG0892: Velocity rows have recorded no model since RETRO0121, so calibration falls back to a July row of another model

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_velocity_row_model.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** sdlc-studio/retros/VELOCITY.md rows RETRO0121-RETRO0129, RPT0014 Calibration
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:52Z

## Summary

VELOCITY.md rows RETRO0121-RETRO0129 carry '-' in the model column, so RPT0014's Calibration reads 'Minutes per point 6.4 - fallback: 0 row(s) for claude-opus-5-5, under 3, so the latest rows of any single model: median of RETRO0028' (claude-opus-4-8, 2026-07-15).

## Steps to Reproduce

1. sprint sign on a run whose meter names claude-opus-5-5. 2. Read the new VELOCITY.md row -> model '-'.

## Proposed Fix

Record the run meter's model on the velocity row, as rows up to RETRO0120 did.

## Acceptance Criteria

- [ ] **AC1** Given a run whose token meter names model claude-opus-5-5, when the close records its velocity row, then the row's model column reads claude-opus-5-5 and the next plan's calibration counts it for that model. Fails on: the current code writes '-'
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_velocity_row_model.py::VelocityRowModelTests::test_the_velocity_row_names_the_run_model
- [ ] **AC2** Given three velocity rows naming claude-opus-5-5, when the next plan prices its batch, then the tokens-per-point calibration rate reads that model's rows and not the fallback to another model's row (the minutes-per-point rate is BG0907). Fails on: the current code's model-less rows (every row since RETRO0121) leave the tokens rate on the fallback
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_velocity_row_model.py::VelocityRowModelTests::test_three_named_rows_end_the_calibration_fallback

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
| 2026-10-02 | qa seat (goal review) | AC2 added: the control beside AC1, so the goal cannot go green on a fixture |
| 2026-10-02 | engineering seat (build, D0305) | AC2 narrowed to the tokens-per-point rate its test checks; the minutes rate still falls back for want of Wall (s) and is BG0907 |
