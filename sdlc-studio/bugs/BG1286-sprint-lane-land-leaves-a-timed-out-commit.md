# BG1286: `sprint lane land` leaves a timed-out commit's hook running while saying it was stopped, and reports a dirty worktree's rebase refusal as a conflict

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1286.md
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

- [ ] **AC1** Given a lane whose pre-commit hook starts a child process and outlasts a shortened `COMMIT_TIMEOUT`, when `sprint lane land` runs, then it exits non-zero with nothing committed and the root's branch as it was, and neither the hook nor its child is alive once the command has returned. Fails on: the hook and the suite it started running on in the worktree after the refusal says they were stopped.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_commit_that_times_out_stops_the_hook_and_its_children
- [ ] **AC2** Given a worktree holding a staged change and an unstaged edit to a file that is not a unit's own story or bug, when `sprint lane land` runs, then it exits 2 before anything is committed, names the unstaged file as the reason, keeps the edit, and says nothing of a conflict or an aborted rebase. Fails on: the lane committed and then stopped with 'the rebase was aborted' and 'Conflicting files: none reported by git'.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_an_unstaged_edit_to_any_other_file_is_refused_by_name_before_the_commit
- [ ] **AC3** Given a lane whose commit conflicts with the root's branch, when `sprint lane land` runs, then the rebase is aborted and the refusal names the conflicting file, as it does today. Fails on: the dirty-tree check or the reworded message swallowing a true conflict.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_rebase_conflict_is_aborted_and_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
