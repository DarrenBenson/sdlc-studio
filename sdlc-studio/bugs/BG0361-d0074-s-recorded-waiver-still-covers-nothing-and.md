# BG0361: D0074's recorded waiver still covers nothing, and record-time validation would accept the same shape again

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; each load-bearing predicate mutation-killed)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

US0525 made the conformance lane read waivers, and the previous sprint's close is still blocked: D0074's scope tail names neither a unit nor a range, so it matches nothing. US0526 validates the RULE half of a waiver subject and not the scope tail, so the exact shape that does nothing would be accepted again today. A waiver that silently covers nothing is worse than a refused one.

## Steps to Reproduce

Reported by a delivery lane during RUN-01KYKVZM; see the summary for the measurement.

## Proposed Fix

See the summary; the remedy is stated with the defect.

## Acceptance Criteria

### AC1: A waiver whose scope tail names no unit is refused at record time

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_decisions.py::WaiverScopeTailTests::test_a_scope_naming_no_unit_is_refused_at_record_time
- **Verified:** yes (2026-07-28)

### AC2: A single id, a range, and an absent tail are all still accepted

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_decisions.py::WaiverScopeTailTests::test_a_range_and_a_single_id_are_accepted
- **Verified:** yes (2026-07-28)

### AC3: The record-time refusal and the run-time matcher answer the same question, asserted as agreement

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_decisions.py::WaiverScopeTailTests::test_the_check_agrees_with_the_consumer_that_resolves_it
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery, replacing the auto-written stated absence the filer produced. Executable, because BG0356/BG0360 made a bug's Verify lines run. |
