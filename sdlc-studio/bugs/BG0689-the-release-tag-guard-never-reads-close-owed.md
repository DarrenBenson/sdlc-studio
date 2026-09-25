# BG0689: The release tag guard never reads close_owed's velocity half, so a retro owing its velocity row does not refuse the tag

> **Status:** Superseded
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Evidence:** BG0668 independent delivery review (qa and engineering seats), RUN-01M2JA6J 2026-09-15; probes in the run's scratchpad drev-BG0668-*.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`release_cut._close_owed_units` reads `close_owed.blocking(report)[`'units'] only; `is_owed` also reads the velocity half. On a corpus where only a retro's velocity row is owed, `close_owed.py` detect exits 1 and tag-check exits 0 with 'no close is owed' - at 3f73ab64 and after BG0668.

## Steps to Reproduce

A baselined corpus whose one retro, dated after the stamp, carries no velocity row and no Velocity-override; detect exits 1, `release_cut.py` tag-check exits 0.

## Proposed Fix

Refuse the tag on blocking()['velocity'] too, naming the retro, or read `is_owed` and report both halves.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `release_cut._close_owed_units` reads `close_owed.blocking(report)[`'units'] only; `is_owed` also reads the velocity half.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: A baselined corpus whose one retro, dated after the stamp, carries no velocity row and no Velocity-override; detect exits 1, `release_cut.py` tag-check exits 0.
- [ ] **AC3** The proposed fix lands, pinned by a test: Refuse the tag on blocking()['velocity'] too, naming the retro, or read `is_owed` and report both halves.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-25 | sdlc | Superseded by US0942: the require-close lane and the tag's close-owed half it describes are retired (US0942 Done) |
