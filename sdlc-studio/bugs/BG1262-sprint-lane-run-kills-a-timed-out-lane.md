# BG1262: `sprint lane run` kills a timed-out lane with no `SIGTERM` first, leaving `index.lock` behind, and leaves four further lane rules unhandled or unpinned

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, changelog.d/BG1262.md
> **Evidence:** run eight (RUN-01M6RZQZ) BG1245 review round 1 ([new] and [pre-existing]), and the orchestrator's friction log (R8-F5)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:37:45Z

## Summary

From BG1245's review, outside its regression (filed separately). (1) At the timeout `_kill_group` sends the group `SIGKILL` with no `SIGTERM` first (`.claude/skills/sdlc-studio/scripts/lib/lanes.py:534`), so a `git add` killed mid-write leaves `<gitdir>/worktrees/<wt>/index.lock` behind (2 of 5 runs of a tight-loop staging child under `--timeout 1`), and the next `git commit` in that worktree, which `lane land` needs, refuses with 'index.lock: File exists'. (2) The grace wait in `_kill_group` (`lanes.py:536`) is pinned by no test: mutant `deadline = time.monotonic() - 1` survives the AC1 test, and the AC1 docstring's mutant 'the staged set read while the group still runs' (`tests/test_lane_run.py:400`) names one no assertion can tell apart. (3) Pre-existing: a CLI that exits, 0 or not, while a background child it started lives on is never group-killed, so the child stages after the record (`staged: [src/lane.py]`, then `src/late.py` in the index, at `fd1c2b5b` and at HEAD); the `run` docstring's 'so nothing it started stages work after the record' (`lanes.py:613`) holds only on the timeout path. (4) Pre-existing: a CLI that cannot exec (a bad shebang) raises an uncaught `FileNotFoundError` after the in-flight marker is taken (`lanes.py:642`), leaving the unit in flight. (5) Pre-existing: `setUp` puts the fake bin in front of the real `PATH` (`tests/test_lane_run.py:148`), so a missing fake resolves to the real harness CLI; a review probe ran the real `codex` once (401, nothing spent). BG1256 (open) covers the unconfined git in the same test module, not these.

## Steps to Reproduce

(1) Run `sprint.py lane run --timeout 1` five times with a fake CLI that loops `git add` on a growing file: at least one run leaves `index.lock`, and `git commit` in the worktree refuses. (2) Apply the deadline mutant and run the AC1 test: green. (3) A fake CLI that starts `(sleep 2; git add src/late.py) &` and exits 0: the record names only `src/lane.py`, then `git diff --cached --name-only` shows `src/late.py`. (4) A fake CLI whose shebang names a missing interpreter: a traceback, and the unit still reads in flight. (5) Remove the fake `codex` from the fixture bin and run the codex case: the binary on the operator's `PATH` runs.

## Proposed Fix

In `_kill_group` send `SIGTERM` to the group, wait the grace for it to empty, then `SIGKILL`, and pin the grace with a child that traps `SIGTERM` and writes a marker; after the CLI exits, kill what is left of its group before the staged set is read; catch the exec failure, release the in-flight marker and refuse naming the CLI path; build the test environment's `PATH` from the fake bin and the system directories git and Python need, never the operator's `PATH`, and refuse in `setUp` when a fake is missing.

## Acceptance Criteria

- [ ] **AC1** Given a lane that times out while its CLI's child traps SIGTERM and writes a marker, when the timeout fires, then the group is sent SIGTERM first and the marker is written before any SIGKILL; and a timed-out lane whose CLI loops `git add` leaves no `index.lock` in its worktree. Fails on: SIGKILL with no SIGTERM first, or the grace mutant `deadline = time.monotonic() - 1` passing the test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneTimeoutTermsFirstTests
- [ ] **AC2** Given a CLI that exits 0 while a background child it started is still running, when the lane records, then that child is killed before the staged set is read and no file it would stage is in the index afterwards. Fails on: a file staged after the record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneLeftoverChildTests
- [ ] **AC3** Given a CLI that cannot be executed (a shebang naming a missing interpreter), `lane run` refuses naming the CLI path and the unit is no longer in flight; and the test module's PATH holds only the fake bin and the system directories git and Python need, so a missing fake fails in setUp rather than reaching a real harness CLI. Fails on: a traceback with the unit left in flight, or the operator's PATH reaching a test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneExecFailureTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-12 | Claude Opus 5.5 (run eleven orchestrator) | Groomed for run eleven (D0469, D0470): criteria rewritten with runnable Verify lines on the at-HEAD triage's evidence |
