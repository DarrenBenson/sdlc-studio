# BG0361: D0074's recorded waiver still covers nothing, and record-time validation would accept the same shape again

> **Status:** Open
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
