# BG1713: Two lanes of one parallel drive wave create their worktrees at the same moment, and git's concurrent worktree add can refuse one, stopping that unit at build

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_worktree_concurrent.py
> **Evidence:** CI run 45068223727 (30eb84a5), job ci 137349078590: test_sprint_drive_wave FAIL with the commondir error
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T22:05:06Z

## Summary

lib/lanes.py `_lane_worktree` runs `git worktree add` with no lock, and sprint.py drive builds a wave's lanes in parallel, so two lanes can add worktrees to the same repository at the same moment. Git does not serialise that: one add can read the other's half-written .git/worktrees/<name>/ entry and fail with 'fatal: failed to read .git/worktrees/lane-us0102/commondir: Success'. The drive then stops that unit at build as a refusal (exit 2) although nothing is wrong with it. Seen in CI run 45068223727 on 30eb84a5, where `test_sprint_drive_wave`'s `test_a_warning_on_a_green_step_stops_the_unit` failed this way; the same module also flaked under load on a local commit the same day.

## Steps to Reproduce

Run sprint.py drive over a wave of two disjoint units with a harness, many times or under load; occasionally one unit stops at build with 'the lane worktree ... could not be created: fatal: failed to read .git/worktrees/lane-<other>/commondir'.

## Proposed Fix

Serialise worktree creation per repository (a lock file under the git common dir held around the add in `_lane_worktree)`, and pin it with a test that adds several lane worktrees from parallel threads and expects every add to succeed.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: lib/lanes.py `_lane_worktree` runs `git worktree add` with no lock, and sprint.py drive builds a wave's lanes in parallel, so two lanes can add worktrees to...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run sprint.py drive over a wave of two disjoint units with a harness, many times or under load; occasionally one unit stops at build with 'the lane worktree ...
- [ ] **AC3** The proposed fix lands, pinned by a test: Serialise worktree creation per repository (a lock file under the git common dir held around the add in `_lane_worktree)`, and pin it with a test that adds...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
