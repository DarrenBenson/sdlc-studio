# BG0509: the close-time-repair split uses day granularity and a global override map, so a same-day terminal is excused and an override never expires

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Two residual defects in US0617/US0618, both reported by the independent review of EP0204 and both pre-existing at the declared base ref. First: `close_time_repairs` compares dates at DAY granularity with a >= test, so a unit that reached terminal EARLIER on the same day as the retro is classified a close-time repair and released from the exit code - contradicting US0617's own definition of after. Second: `close_repair_overrides` scans every retro into one global map with no scoping to a run, so a recorded override forgives that unit permanently in all later runs rather than for the close that needed it.

## Steps to Reproduce

Date a retro 2026-02-01 with a Batch naming BG0001, record BG0005 terminal on 2026-02-01, and run `close_owed` detect: it exits 0 where the same fixture before US0617 exited 1. For the override half, record a Close-repair-override in one retro and observe it still forgiving the same unit in a later run's detect.

## Proposed Fix

Carry a timestamp rather than a day for the terminal record, or compare strictly greater when the dates are equal and the retro's own commit is later. Scope the override to the run that recorded it, keyed on the retro or run id, so an exception expires with the close it was granted for.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Two residual defects in US0617/US0618, both reported by the independent review of EP0204 and both pre-existing at the declared base ref.
- [ ] Following the recorded steps no longer reproduces the defect: Date a retro 2026-02-01 with a Batch naming BG0001, record BG0005 terminal on 2026-02-01, and run `close_owed` detect: it exits 0 where the same fixture before...
- [ ] The proposed fix lands, pinned by a test: Carry a timestamp rather than a day for the terminal record, or compare strictly greater when the dates are equal and the retro's own commit is later.

## Impact

The first releases a unit from the ledger's exit code on the strength of a same-day coincidence, which is the direction that under-reports. The second makes an exception permanent, which is how a deliberate one-off becomes routine - the exact thing US0618 states it exists to prevent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
