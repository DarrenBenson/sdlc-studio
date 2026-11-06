# BG1255: US1123's signed-page test runs git without the confined environment, so the push gate's unconfined-git sweep is red

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py
> **Evidence:** run seven (RUN-01M6RAP7) push of a5df01de, refused at the push boundary by devserver1's full suite, 2026-11-06
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T15:24:59Z

## Summary

The push of a5df01de was refused by the full suite on devserver1: `test_gitutil.py::UnconfinedRawGitCallSweepTests::test_no_module_calls_git_without_a_confined_environment` reports `{'test_report_usd': (1, 0)}`. `test_report_usd.py` (about line 320, US1123's round-two pin of the signed page's price table) calls `subprocess.run(["git", ...])` with no `env=gitutil.git_env()`, so a hook's or an outer repository's `GIT_DIR` can redirect it. The commit hook did not select the sweep.

## Steps to Reproduce

Run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py::UnconfinedRawGitCallSweepTests -q` at a5df01de.

## Proposed Fix

Pass `env=gitutil.git_env()` to the test's git calls, as `test_critic_self_check_refusal.py` does.

## Acceptance Criteria

- [ ] **AC1** No test module calls git without a confined environment, `test_report_usd.py` included.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gitutil.py::UnconfinedRawGitCallSweepTests
  - **Verified:** yes (2026-11-06)
- [ ] **AC2** The signed-page price-table pin still passes with its git calls confined.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Criteria authored with Verify checks for run seven |
