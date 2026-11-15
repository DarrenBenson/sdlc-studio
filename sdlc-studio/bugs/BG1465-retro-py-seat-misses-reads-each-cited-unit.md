# BG1465: retro.py seat_misses reads each cited unit's file uncached, so an unbounded window does not finish in ten minutes

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py, changelog.d/BG1465.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** QA seat's round-1 and round-2 reviews of US1064, run thirteen.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:18:00Z

## Summary

`seat_misses` calls `sdlc_md.find_by_id`, uncached, for every cited ledger unit of every bug in the window (retro.py near line 1604). Over the first dated retro's unbounded window on this repository's bugs, retro.py seats did not finish inside a ten-minute probe. A close or a seat report that reads that window stalls.

## Steps to Reproduce

1. Run retro.py seats over a window starting before the first dated retro on this repository.
2. It does not finish in ten minutes.

## Proposed Fix

Resolve each unit id once per call (a dict of id to path, or one directory scan), and add a test that bounds the lookups per unit.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `seat_misses` calls `sdlc_md.find_by_id`, uncached, for every cited ledger unit of every bug in the window (retro.py near line 1604).
- [ ] **AC2** The proposed fix lands, pinned by a test: Resolve each unit id once per call (a dict of id to path, or one directory scan), and add a test that bounds the lookups per unit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
