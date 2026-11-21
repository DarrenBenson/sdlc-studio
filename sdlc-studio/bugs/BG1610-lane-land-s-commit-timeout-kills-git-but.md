# BG1610: lane land's commit timeout kills git but leaves the hooks' test run running orphaned, holding the host's CPU after the land reports nothing committed

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1610.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_commit_timeout_group.py
> **Evidence:** run eighteen, 2026-11-19, lane L1 (US1192, US1193): the land stopped at 1800s; 23 minutes later the orphaned commit-msg hook (parent 990) and eight pytest workers were still running in the lane's worktree, at load 15 on 8 cores, and were stopped by hand
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T13:20:46Z

## Summary

`lib/lanes.py` `_commit` runs `git commit` through `subprocess.run(..., timeout=COMMIT_TIMEOUT)`. On the timeout Python kills only the git process; the commit-msg hook it spawned, its `gate.py --run-tests` and the pytest-xdist workers are reparented and keep running. The land prints that the hooks were stopped and nothing was committed, but the orphaned suite goes on loading the host, so a retried land, or the next lane's, meets the same load and can time out again.

## Steps to Reproduce

On a loaded host, run `sprint.py lane land --worktree <wt> --units <id>` whose commit hooks take longer than 1800s. After the land exits with 'the commit's hooks ran past 1800s and were stopped', `ps -eo pid,ppid,args` still lists `.githooks/commit-msg`, `gate.py --run-tests` and the pytest workers, with the hook's parent now the user's init process.

## Proposed Fix

Start the commit in its own session (`start_new_session=True`) and, on the timeout, kill the whole process group before raising, so 'were stopped' is true; pin it with a hook stub that spawns a long-lived child.

## Acceptance Criteria

- [ ] **AC1** Given a commit-msg hook stub that spawns a long-lived child and a shrunk `COMMIT_TIMEOUT`, when `sprint.py lane land --worktree <wt> --units <id>` runs and the bound fires, then it reports nothing committed and no hook or child process of the commit is left running, so 'were stopped' is true. Fails on: the hook and its children are reparented to init and keep running after the land exits.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_commit_timeout_group.py::LandCommitTimeoutKillsHooksTests
  - **Verified:** yes (2026-11-21)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-one) |
