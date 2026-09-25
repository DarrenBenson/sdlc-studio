# BG0753: The test suite leaks temporary directories into /tmp

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/tests/conftest.py, .claude/skills/sdlc-studio/scripts/tests/conftest.py, tools/skill-tests.sh, tools/tests/test_lean_tmp_hygiene.py, changelog.d/BG0753.md, conftest.py
> **Evidence:** RUN-01M3891F: /tmp at 1048576/1048576 inodes; lane B commit failed with 32 ENOSPC errors
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Test runs leave `tmp*` directories behind: about 44,000 were seen in one sprint, and /tmp ran out of inodes mid-run, failing a commit's suites with ENOSPC (Errno 28).

Measured 2026-09-25 at 65cdf1ca: one pytest run of both trees (`-n 12`, TMPDIR pointed at an empty directory) left 225 top-level entries and about 1,900 inodes behind. 212 were directories: 76 bare `tmpXXXXXXXX`, and prefixed ones from test_sprint.py (`goal_review_`, `close_gate_`), test_known_issues.py (`known_issues_`, `bar_population_`, `release_bar_`) and test_verify_corpus.py (`verify_corpus_`, `baseline_identity_`). 14 test modules call `mkdtemp` with no `rmtree` or `addCleanup` anywhere. /tmp holds 23,329 `tmp*` entries today.

Chasing each fixture is 14+ modules of edits, and a future fixture re-opens the leak. The criteria instead ask that every runner confine a run's temporary files to a directory it removes, which fixes the code path rather than adding a check (LC-008). No new refusal: the runner cleans, and the test pins that it does.

## Steps to Reproduce

1. Run `bash tools/skill-tests.sh` several times. 2. `ls -d /tmp/tmp* | wc -l` grows each run.

## Proposed Fix

Give each test run its own temporary directory and remove it when the run ends, pass or fail: `tempfile.tempdir` and `TMPDIR` for pytest sessions over either tree, and the same for `tools/skill-tests.sh`'s unittest path. Subprocesses then inherit it.

## Acceptance Criteria

- [ ] **AC1** Given a probe test module holding a test that leaks a `tempfile.mkdtemp()` directory, a test whose subprocess leaks one, and a failing test, when it runs under pytest in each test tree, serially and under `-n 2`, with TMPDIR at an empty directory, then that directory is empty after the session. Fails on: setting only `os.environ["TMPDIR"]` after `tempfile` has cached its directory; covering only `tools/tests`, the one tree with a conftest today; cleanup that runs only when the session is green.
  - **Verify:** pytest tools/tests/test_lean_tmp_hygiene.py::TmpHygieneTests::test_a_pytest_session_in_either_tree_leaves_no_temp_dir_behind
- [ ] **AC2** Given the same probe module, when `tools/skill-tests.sh`'s unittest path runs it with TMPDIR at an empty directory, then that directory is empty afterwards and the script's exit status still reports the failing test. Fails on: a conftest-only fix, which unittest never loads; a trap that removes the directory but replaces the suite's exit status with its own.
  - **Verify:** pytest tools/tests/test_lean_tmp_hygiene.py::TmpHygieneTests::test_the_unittest_runner_leaves_no_temp_dir_behind_and_keeps_its_verdict

## Impact

Test runs leave `tmp*` directories behind: about 44,000 were seen in one sprint, and /tmp ran out of inodes mid-run, failing a commit's suites with ENOSPC (Errno 28).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (one run of both suites left 225 entries, about 1,900 inodes, in an isolated TMPDIR); proposed fix moved from per-fixture cleanup plus a leak check to runner-level confinement, with no new refusal; criteria rewritten Given/When/Then with executable Verify lines in a new test_lean module, each naming the wrong fix it fails on; Affects set to the runners; 3 points stand |
