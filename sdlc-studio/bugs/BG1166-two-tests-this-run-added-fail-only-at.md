# BG1166: Two tests this run added fail only at the push gate: one shells out to git unconfined, one reads ignore rules through the gate host's symlinked .local

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate_budget.py, tools/tests/test_lean_trd_refresh.py, changelog.d/BG1166.md
> **Evidence:** devserver1 boundary-suite-last.log for 1fbb6a46: FAILED test_gitutil.py::UnconfinedRawGitCallSweepTests::test_no_module_calls_git_without_a_confined_environment, and SUBFAILED test_lean_trd_refresh.py::TrdStorageTests::test_the_run_lifecycle_reaches_sign for sdlc-studio/.local/run-state.json and sdlc-studio/.local/run-archive/*.json.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T08:23:24Z

## Summary

The push of 1fbb6a46 (2026-11-01) was refused on devserver1. 3 of 8338 failed, all from two units already closed in this run. (1) BG1065's b82dcc36 added `test_the_recorded_commit_is_one_this_repository_holds` to .claude/skills/sdlc-studio/scripts/tests/`test_gate_budget.py`, which calls `subprocess.run(["git", ...])` with no confined environment. `test_gitutil.py`::UnconfinedRawGitCallSweepTests holds that count at zero and fails with {'`test_gate_budget`': (1, 0)}. The commit hook never selected `test_gitutil`, so it surfaced only at push. (2) US1100's cd61ddab added TrdStorageTests::`test_the_run_lifecycle_reaches_sign` to tools/tests/`test_lean_trd_refresh.py.` Its `_ignored` runs `git check-ignore -q --no-index sdlc-studio/.local/...`. tools/remote-gate.sh:241 makes the gate host's `sdlc-studio/.local` a symlink to its per-clone state, and git refuses the path ('fatal: pathspec ... is beyond a symbolic link', rc 128). So `_ignored` reads False and both `.local` subtests fail. Both pass locally, where `.local` is a directory or absent.

## Steps to Reproduce

1. `pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py -k UnconfinedRawGitCallSweepTests`: fails on `test_gate_budget.`
2. Clone the repo, `ln -s <dir> sdlc-studio/.local`, then `git check-ignore -q --no-index sdlc-studio/.local/run-state.json`: rc 128.
3. Run tools/tests/`test_lean_trd_refresh.py`::TrdStorageTests in that clone: two subtests fail.

## Proposed Fix

Route the gate-budget commit check through tests/gitutil.git. Have `_ignored` judge a path by the ignore rules alone, so the answer does not depend on whether `.local` exists, is a directory or is a symlink, for example by asking check-ignore in a scratch repository that holds only the tracked .gitignore files.

## Acceptance Criteria

- [ ] **AC1** `test_gitutil.py`::UnconfinedRawGitCallSweepTests passes, with `test_gate_budget` making no unconfined git call.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py -k UnconfinedRawGitCallSweepTests
- [ ] **AC2** TrdStorageTests passes when sdlc-studio/.local is a symlink, as on the gate host, when it is a directory, and when it is absent, and still fails when the TRD's Run state table says a tracked path is kept in `.local`.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py -k TrdStorageTests

## Impact

main cannot be pushed: the boundary gate refuses every push until both are fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
