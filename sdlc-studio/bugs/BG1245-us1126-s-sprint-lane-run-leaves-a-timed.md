# BG1245: US1126's `sprint lane run` leaves a timed-out lane's children staging in the worktree, an in-flight marker after its own refusal, and a branch that refuses the next run

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US1126.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, changelog.d/BG1245.md
> **Evidence:** run seven (RUN-01M6RAP7) US1126 review rounds 1 and 2
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:36:19Z

## Summary

Run seven, US1126 rounds 1 and 2 (round 2 APPROVE; the round-1 blocking finding is closed). Re-executed in round 2 and still open: (1) A timed-out lane's CLI children outlive the timeout: `subprocess.run(cmd, ..., timeout=timeout)` (`lib/lanes.py:553`) starts no process group and kills none (no `start_new_session` or `killpg` in the module). Probe: a fake codex whose child writes a file and runs `git add -A` at 4 s, with `--timeout 2`: exit 1, unmetered `timeout`, record `staged: []`, and the late write landed afterwards, so `lane land` would commit work the record says was never staged; the AC3 test mocks `TimeoutExpired`. (2) A refusal inside `lanes.run` leaves the unit's in-flight marker: `lane run --worktree <missing>` exits 2 and the run state holds `lanes_in_flight: [US0101]` (`sprint.py:9133` takes the marker before `lanes.run` refuses), though exit 2 is documented as a refusal before the CLI ran. (3) `_lane_worktree` always passes `-b lane-<unit>` (`lib/lanes.py:506`), so once a lane worktree is removed without `lane land`, the next `lane run` of that unit exits 2 until the branch is deleted by hand. (4) The flags that let each builder write are unpinned: dropping codex `--sandbox workspace-write` (:467), codex `--add-dir` (:470), copilot `--allow-all-tools` (:472) or cursor `--force` (:465) each survive all six tests of `test_lane_run.py`. (5) The `tokens <= 0` guard in `run_reading` (:640) is unpinned (mutant `if False:` survives). (6) `help/sprint.md:564` and `changelog.d/US1126.md:6` name the default worktree `lane-<unit>`, but it is created lowercased (`lib/lanes.py:502`, `lane-us0101`). (7) Introduced by the per-session repair: in a multi-session return the unmetered warning (`lib/lanes.py:629`) does not name the session's record, so the operator cannot tell which session went unpriced.

## Steps to Reproduce

1. Put a fake `codex` on PATH whose child sleeps 4 s, writes a file and stages it, and run `sprint.py lane run` for a unit with `--timeout 2`: after 5 s the worktree's index holds the file while the record's `staged` is empty. 2. Run `sprint.py lane run --worktree /nonexistent` for a unit: exit 2, and the run state's `lanes_in_flight` names it. 3. Remove a lane worktree with `git worktree remove` and run `lane run` for the same unit: exit 2, the branch already exists.

## Proposed Fix

Start the CLI with `start_new_session=True` and kill its process group on timeout (as BG1190 proposes for verifiers), then read the staged set after the kill; take the in-flight marker only after `lanes.run`'s own refusals pass, or clear it on exit 2; reuse an existing `lane-<unit>` branch that has no worktree instead of refusing; pin each builder flag and the zero-token guard; name the worktree as created (lowercased) in the help; name the session's record in the unmetered warning.

## Acceptance Criteria

- [ ] **AC1** Given a fake `codex` on PATH whose child process writes and stages a file 4 s after start, when `sprint.py lane run` runs it with `--timeout 2`, then the CLI's whole process group is killed, no file lands in the worktree after the command returns, and the record's `staged` is read after the kill and matches the worktree's index. Fails on: `subprocess.run` in `lib/lanes.py` started without `start_new_session=True` and no `killpg` on `TimeoutExpired`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_a_timed_out_lane_s_children_are_killed
- [ ] **AC2** Given `sprint.py lane run --worktree /nonexistent` for a unit, then it exits 2 and the run state's `lanes_in_flight` does not name the unit; and given a lane worktree removed with `git worktree remove` without `lane land`, a second `lane run` of the unit reuses its existing `lane-<unit>` branch and exits 0. Fails on: the in-flight marker taken in `sprint.py` before `lanes.run`'s refusals pass, or `_lane_worktree` always passing `-b`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_a_refused_or_repeated_lane_run_leaves_no_stale_state
- [ ] **AC3** Given each builder harness's headless command, then it carries the flag that lets it write (codex `--sandbox workspace-write` and `--add-dir`, copilot `--allow-all-tools`, cursor `--force`), and a lane record reporting zero input, output and cache write gives `run_reading` no priced reading. Fails on: any one of the four flags dropped from `headless_command`, or the `tokens <= 0` guard in `run_reading` replaced by `if False:`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_each_builder_can_write_and_a_zero_reading_is_not_priced
- [ ] **AC4** Given a multi-session return in which one session is unmetered, then the warning names that session's record path; and `help/sprint.md` and `changelog.d/US1126.md` name the default worktree as it is created, lowercased (`lane-us0101`). Fails on: the warning at `lib/lanes.py:629` naming only the unit, or the help keeping `lane-<unit>` in upper case.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_the_unmetered_warning_names_its_session_record

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria with Verify checks, Points and Affects |
