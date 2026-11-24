# BG1695: lane land names a conflicting path that holds a space as two paths

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_replay.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, changelog.d/BG1695.md
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

- [ ] **AC1** Given a lane and main that both edit `docs/release notes.md` so the replay conflicts, when `sprint.py lane land` refuses, then the refusal's Conflicting files names `docs/release notes.md` once. Fails on: `.stdout.split()` at the replay refusal names `docs/release` and `notes.md`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_replay.py::LaneLandReplayTests::test_a_replay_conflict_names_a_path_holding_a_space_once
- [ ] **AC2** Given the same conflict met by `_rebase` (a lane committed on its branch), when lane land refuses, then it names `docs/release notes.md` once. Fails on: `_rebase` splits the same listing on whitespace.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_replay.py::LaneLandReplayTests::test_a_rebase_conflict_names_a_path_holding_a_space_once
- [ ] **AC3** Given a conflict in `plain.md`, when either refusal fires, then it names `plain.md` alone (positive control). Fails on: a NUL split that returns an empty trailing name.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_replay.py::LaneLandReplayTests::test_a_replay_conflict_still_names_an_ordinary_path
- [ ] **AC4** Given a lane run whose worktree stages `docs/release notes.md`, when `sprint.py lane run` records and prints its staged paths, then the path is recorded and printed once. Fails on: `lanes._run` reads `diff --cached --name-only` with `.split()`, the same split AC1 and AC2 remove.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_a_staged_path_holding_a_space_is_recorded_once

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: the one reproduction is now two criteria (replay and `_rebase`) and a control; both sites (lanes.py:390 and :475) still split on whitespace at HEAD |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's LN lane: AC4 added for the third whitespace split, the lane run's staged-path read in lanes._run (D0561, fix in the unit) |
