# BG1261: After BG1245 a hard kill of `sprint.py`'s process group no longer reaches a running lane, whose CLI runs on in the worktree with no timeout over it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py
> **Evidence:** run eight (RUN-01M6RZQZ) BG1245 review round 1 ([regression]), and the orchestrator's friction log (R8-F5)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:37:39Z

## Summary

Regression from BG1245. Its AC1 mandated `start_new_session=True` for the lane's CLI (`.claude/skills/sdlc-studio/scripts/lib/lanes.py:591`), so the CLI and its children sit in a session of their own. A `SIGKILL` to `sprint.py`'s own process group (a supervisor's hard kill, `timeout -s KILL`) now kills `sprint.py` alone: the CLI and its children run on with no timeout left over them and stage work into the worktree that no record names. At `fd1c2b5b` the same group kill took the CLI and its children with it. `SIGTERM`, `SIGINT` and `SIGHUP` to the pid or the group are reaped, so the reviewer did not hold the gate. Neither `help/sprint.md:567` nor `changelog.d/BG1245.md` states the limit.

## Steps to Reproduce

Start `sprint.py lane run` under `setsid` for a unit whose fake CLI sleeps and then stages a file, and send `SIGKILL` to that group (`kill -KILL -<pgid>`): `sprint.py` is gone, `ps` still shows the fake CLI, and the file appears in the lane worktree's index once it wakes. At `fd1c2b5b` the fake dies with the group.

## Proposed Fix

Give the lane a parent-liveness watchdog that kills the lane's group when `sprint.py` dies (a pipe held open by `sprint.py` whose end-of-file the watchdog reads, or a poll of the parent pid), and pin it with a test that hard-kills the caller's group and asserts the fake CLI is gone and stages nothing. State the behaviour in `help/sprint.md`.

## Acceptance Criteria

- [ ] **AC1** Following the recorded steps no longer reproduces the defect: Start `sprint.py lane run` under `setsid` for a unit whose fake CLI sleeps and then stages a file, and send `SIGKILL` to that group (`kill -KILL -<pgid>`)...
- [ ] **AC2** The proposed fix lands, pinned by a test: Give the lane a parent-liveness watchdog that kills the lane's group when `sprint.py` dies (a pipe held open by `sprint.py` whose end-of-file the watchdog...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
