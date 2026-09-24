# BG0751: Open findings in a sprint report use an inclusive window end

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** US0885 review finding 4 (read, not executed), RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_open_findings` compares a finding's stamp with `window_end` using `when > hi`, so a finding stamped in the generation second after the page enters only the re-derivation; a finding with only a date-level Created fallback races across the whole day. It feeds the fingerprint through known issues.

## Steps to Reproduce

1. File a report. 2. In the same second (or the same day, for a Created-only finding) file a bug. 3. `check` can read INVALID.

## Proposed Fix

Use the half-open bound (`when >= hi`) for timestamped stamps, and exclude date-only stamps on the generation day.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_open_findings` compares a finding's stamp with `window_end` using `when > hi`, so a finding stamped in the generation second after the page enters only the...
- [ ] **AC2** The proposed fix lands, pinned by a test: Use the half-open bound (`when >= hi`) for timestamped stamps, and exclude date-only stamps on the generation day.

## Impact

`_open_findings` compares a finding's stamp with `window_end` using `when > hi`, so a finding stamped in the generation second after the page enters only the re-derivation; a finding with only a date-level Created fallback races across the whole day.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Recurred after a seal: RPT0008 checked VALID at dcbee3d4, then BG0762, filed the same day after the seal, entered the re-derivation's known issues through the date-level Created fallback, and `check` now reads the signed page INVALID. Nothing about the run changed |
