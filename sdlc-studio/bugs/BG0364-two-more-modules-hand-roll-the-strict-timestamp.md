# BG0364: Two more modules hand-roll the strict timestamp parser BG0353 just fixed in telemetry

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/loop_guard.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

transition.py and `loop_guard.py` each carry their own Z-only stamp parser, so the offset-bearing timestamps BG0353 made telemetry accept are still rejected there. One rule, three implementations, two of them now wrong - the class the carried lesson about enumerated rules covers.

## Steps to Reproduce

Reported by a delivery lane during RUN-01KYKVZM; see the summary for the measurement.

## Proposed Fix

See the summary; the remedy is stated with the defect.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
