# BG1256: test_lane_run.py runs git unconfined through a local name and inside its fake CLI script, where the unconfined-git sweep cannot see it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py
> **Evidence:** run seven (RUN-01M6RAP7) BG1255 review round 1
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T15:35:05Z

## Summary

BG1255's reviewer found two unconfined git calls in `.claude/skills/sdlc-studio/scripts/tests/test_lane_run.py` (from US1126, 2c8d0c40): one at about line 286 called through a local name, `real`, and one at about line 61 inside the FAKE script string. `test_gitutil.py::UnconfinedRawGitCallSweepTests` cannot see either. With `GIT_INDEX_FILE` set to a probe file, as a git hook sets it, the timeout case wrote `src/lane.py` into that index and failed at about line 301; without it the case passes. So BG1255's AC1 (no test module calls git unconfined) claims more than its sweep proves.

## Steps to Reproduce

Set `GIT_INDEX_FILE` to a scratch file and run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py -q`.

## Proposed Fix

Pass `gitutil.git_env()` to both calls (the fake script's environment included), and widen the sweep's detector to see git called through a local alias or inside a generated script.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1255's reviewer found two unconfined git calls in `.claude/skills/sdlc-studio/scripts/tests/test_lane_run.py` (from US1126, 2c8d0c40): one at about line 286...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Set `GIT_INDEX_FILE` to a scratch file and run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py -q`.
- [ ] **AC3** The proposed fix lands, pinned by a test: Pass `gitutil.git_env()` to both calls (the fake script's environment included), and widen the sweep's detector to see git called through a local alias or...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
