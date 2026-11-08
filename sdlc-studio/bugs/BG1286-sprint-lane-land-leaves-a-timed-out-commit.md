# BG1286: `sprint lane land` leaves a timed-out commit's hook running while saying it was stopped, and reports a dirty worktree's rebase refusal as a conflict

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg B; repro under scratchpad rel63/legs/scratch-b/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:07:53Z

## Summary

When the commit's hooks run past `COMMIT_TIMEOUT`, subprocess.run kills only `git commit`. The hook and its children (the test suite) run on in the worktree. The refusal says the hooks 'were stopped', and a re-run then commits while the orphaned hook still runs. `lane run` and `verify_ac` kill the whole process group; this path does not. BG1262 covers the lane run kill, not this commit path. Second (lanes.py:159, `_rebase`): If the builder leaves any unstaged change in the worktree, git refuses the rebase before it starts. The lane still commits and then stops with a message that says 'the rebase was aborted' and 'Conflicting files: none reported by git', which reads as a conflict. Only git's own lines underneath give the real cause.

## Steps to Reproduce

bash rel63/legs/scratch-b/`land_timeout.sh` <scratch-b> (`COMMIT_TIMEOUT` patched to 3, pre-commit hook `sleep 40`). Observed: 'the commit's hooks ran past 3s and were stopped ...', exit 1, then 'hook still alive: yes'. No index.lock was left. Second: bash rel63/legs/scratch-b/`land_dirty.sh` <scratch-b>, case A. Observed: 'rebasing lane-x onto main failed, so the rebase was aborted ... Conflicting files: none reported by git ...' followed by 'error: cannot rebase: You have unstaged changes.', exit 1.

## Proposed Fix

Run the commit through Popen with `start_new_session`=True. On timeout, send the group SIGTERM, then SIGKILL after a grace period, as `lanes._run_in_group` and `_kill_group` do. Second: Before committing, check `git diff --quiet` in the worktree and refuse with exit 2, naming the unstaged files, so nothing is committed. Otherwise tell the dirty-tree case apart from a conflict in the message.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: When the commit's hooks run past `COMMIT_TIMEOUT`, subprocess.run kills only `git commit`.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: bash rel63/legs/scratch-b/`land_timeout.sh` <scratch-b> (`COMMIT_TIMEOUT` patched to 3, pre-commit hook `sleep 40`).
- [ ] **AC3** The proposed fix lands, pinned by a test: Run the commit through Popen with `start_new_session`=True.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
