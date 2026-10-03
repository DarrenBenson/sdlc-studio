# BG0907: Calibration's minutes per point falls back to a July row because velocity rows carry no wall time

> **Status:** In Progress
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_velocity_row_wall.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Evidence:** BG0892 QA review round 1 (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T13:58:08Z

## Summary

`retro.minutes_per_point` reads each velocity row's Wall (s); rows RETRO0121 onward record none, so even rows that name the run's model leave the minutes rate on the fallback ('0 row(s) for claude-opus-5-5 ... median of RETRO0028', 6.4 min/pt) while the tokens rate measures on the newest rows.

## Steps to Reproduce

1. Re-record RETRO0127-RETRO0129 so they name claude-opus-5-5. 2. sprint plan -> tokens measured on claude-opus-5-5, minutes still fallback median of RETRO0028.

## Proposed Fix

Record the run's wall-clock seconds on the velocity row at the close, as earlier rows did, so the minutes rate measures on recent rows.

## Acceptance Criteria

- [ ] **AC1** Given three velocity rows naming claude-opus-5-5 recorded by the close, when the next plan prices its batch, then the minutes-per-point rate reads measured on claude-opus-5-5 and not the fallback. Fails on: the current rows carry no Wall (s) and the minutes rate falls back to RETRO0028
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_velocity_row_wall.py::VelocityRowWallTests::test_the_minutes_rate_measures_on_recent_named_rows
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
| 2026-10-03 | engineering seat | sprint.py added to Affects: the round-1 repair fixed the capacity floor there (D0321) |
