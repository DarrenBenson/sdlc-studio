# BG0748: The report's DORA window is second-resolution, so a same-second commit reads the report INVALID

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py
> **Verification depth:** functional (the criteria drive `build_report` over a real git repository with a same-second commit and CI run; the real close, commit and sign read VALID five times of five, and minute and hour floors of the bound are killed)
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

When the paperwork commit lands in the same second the report was generated, the DORA window drifts the fingerprint and `sprint_report.py check` reads INVALID for any outcome, achieved included. A 1.5s gap makes it VALID. Found by the US0878 reviews on RUN-01M36R3D.

## Steps to Reproduce

Generate a report, commit the paperwork within the same second, sign, run `sprint_report.py check`: INVALID for achieved, partial and missed alike.

## Proposed Fix

Bound the DORA window by the report's generation instant at sub-second resolution, or exclude commits at or after `generated_at.`

## Acceptance Criteria

- [x] **AC1** The behaviour described is corrected: When the paperwork commit lands in the same second the report was generated, the DORA window drifts the fingerprint and `sprint_report.py check` reads INVALID...
- [x] **AC2** Following the recorded steps no longer reproduces the defect: Generate a report, commit the paperwork within the same second, sign, run `sprint_report.py check`: INVALID for achieved, partial and missed alike.
- [x] **AC3** The proposed fix lands, pinned by a test: Bound the DORA window by the report's generation instant at sub-second resolution, or exclude commits at or after `generated_at.`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::WindowRaceTests
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Fixed by US0885 (RUN-01M3891F): the story's criteria are this bug's proposed fix, and its selectors verify it here |
