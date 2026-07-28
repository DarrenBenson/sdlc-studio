# BG0362: A retro whose Batch line is prose yields an empty sprint report - the latest sprint reads zero units

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; predicates mutation-killed)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

The report parses the retro's Batch line to find the units, and a line written as prose rather than as ids produces no units at all. The report then states the sprint delivered nothing rather than that it could not read the batch, which is an empty measurement presented as a finding.

## Steps to Reproduce

Reported by a delivery lane during RUN-01KYKVZM; see the summary for the measurement.

## Proposed Fix

See the summary; the remedy is stated with the defect.

## Acceptance Criteria

### AC1: A Batch line naming no units reads as UNREADABLE, not as nothing delivered

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::UnreadableBatchTests::test_no_units_reads_as_unreadable_not_as_nothing_delivered
- **Verified:** yes (2026-07-28)

### AC2: A readable batch still reports its count, so the carve-out does not swallow the normal case

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::UnreadableBatchTests::test_a_readable_batch_still_reports_its_count
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery. |
