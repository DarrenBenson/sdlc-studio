# BG1256: test_lane_run.py runs git unconfined through a local name and inside its fake CLI script, where the unconfined-git sweep cannot see it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py, changelog.d/BG1256.md
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

- [ ] **AC1** Given `GIT_INDEX_FILE` set to a scratch file, as a git hook sets it, when a lane run and its fake CLI stage a file in the timeout case, then the case passes and the scratch index is never written. Fails on: `src/lane.py` staged into the caller's index.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_a_callers_git_index_is_never_written_by_a_lane_or_its_fake_cli
- [ ] **AC2** Given a module that runs git with no `env` through a local name bound to a subprocess runner, when the unconfined-git detector reads it, then the call is counted, and the same call passing an `env` is not. Fails on: a count of zero for the aliased call.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py::UnconfinedRawGitCallSweepTests::test_the_detector_counts_a_call_through_a_local_name
- [ ] **AC3** Given a module holding a generated script whose text runs git with no `env`, when the detector reads it, then the script's call is counted, while a string that only mentions git is not. Fails on: git inside a generated script staying invisible to the sweep.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py::UnconfinedRawGitCallSweepTests::test_the_detector_counts_git_run_inside_a_generated_script

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
