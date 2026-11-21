# BG1695: lane land names a conflicting path that holds a space as two paths

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_replay.py, changelog.d/BG1695.md
> **Evidence:** lanes.py:387 and :469 split conflict names with .stdout.split(); sdlc-studio/reviews/verdicts/BG1448/0cb4f8185b45-b6d89ec7.txt records it [pre-existing].
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T21:14:37Z

## Summary

When a lane's replay or rebase meets a conflict, lib/lanes.py names the conflicting files from git's name listing with .stdout.split() (the replay refusal at lanes.py:387 and `_rebase` at lanes.py:469), which splits on any whitespace. A conflicting path holding a space, such as 'docs/release notes.md', is named as two paths in the refusal, and the drive's conflict reader (`drive._CONFLICT)` reads two files that do not exist. Confirmed by the qa seat in run twenty-one's BG1448 review as already true at the run base.

## Steps to Reproduce

1. In a fixture, make a lane whose staged change and main both edit 'docs/release notes.md' so they conflict. 2. Run sprint.py lane land on it. 3. The refusal names 'docs/release' and 'notes.md' as two conflicting files.

## Proposed Fix

List the conflicting names with git diff --name-only --diff-filter=U -z and split on NUL in both places, decoding each with os.fsdecode as `_loose` does.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: When a lane's replay or rebase meets a conflict, lib/lanes.py names the conflicting files from git's name listing with .stdout.split() (the replay refusal at...
- [ ] **AC2** The proposed fix lands, pinned by a test: List the conflicting names with git diff --name-only --diff-filter=U -z and split on NUL in both places, decoding each with os.fsdecode as `_loose` does.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
