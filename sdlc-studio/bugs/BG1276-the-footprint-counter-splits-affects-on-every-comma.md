# BG1276: The footprint counter splits Affects on every comma, so a path inside a bracketed note is dropped from the unit's file count

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** run eight (RUN-01M6RZQZ) BG1274 round-2 QA verdict, pre-existing item
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T21:39:23Z

## Summary

`_declared_tokens` in `engagement_floor.py` splits the Affects field on every comma before it strips a trailing note, so a declaration such as `a.py (with b.py, c.py)` loses its note's paths from the footprint count. CR0021, CR0141 and CR0155 are affected in this tree. Staged-file ownership is not affected: the hook and the close guard read `declared_keys` since BG1274. Predates run eight (CR0229, 06a65b06).

## Steps to Reproduce

Count the footprint of CR0155 with `engagement_floor.py` and compare it with the files its Affects names.

## Proposed Fix

Split on commas outside brackets, the way `declared_keys` does, and pin the three shapes in `test_engagement_floor.py`.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_declared_tokens` in `engagement_floor.py` splits the Affects field on every comma before it strips a trailing note, so a declaration such as `a.py (with...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Count the footprint of CR0155 with `engagement_floor.py` and compare it with the files its Affects names.
- [ ] **AC3** The proposed fix lands, pinned by a test: Split on commas outside brackets, the way `declared_keys` does, and pin the three shapes in `test_engagement_floor.py`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
