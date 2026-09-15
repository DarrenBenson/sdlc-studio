# BG0688: gate --require-close still counts close-owed's raw owed rows, refusing an override the tag guard and the detector now honour

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** BG0668 independent delivery review (qa and engineering seats), RUN-01M2JA6J 2026-09-15; probes in the run's scratchpad drev-BG0668-*.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`gate._close_owed` returns the count of `close_owed`'s raw owed list, so on a corpus whose only uncovered unit is a same-day close-time repair carrying a recorded Close-repair-override it reports 1, blocking, while `close_owed.is_owed` is False and `release_cut` tag-check (after BG0668) passes. This is BG0518's split at a third site.

## Steps to Reproduce

Build BG0668 AC1's corpus; run gate.py --require-close: it refuses on the overridden repair; `close_owed.py` detect exits 0.

## Proposed Fix

Read `close_owed.blocking(report)` (units and velocity) in `gate._close_owed`, the predicate `is_owed` reads.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `gate._close_owed` returns the count of `close_owed`'s raw owed list, so on a corpus whose only uncovered unit is a same-day close-time repair carrying a...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Build BG0668 AC1's corpus; run gate.py --require-close: it refuses on the overridden repair; `close_owed.py` detect exits 0.
- [ ] **AC3** The proposed fix lands, pinned by a test: Read `close_owed.blocking(report)` (units and velocity) in `gate._close_owed`, the predicate `is_owed` reads.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
