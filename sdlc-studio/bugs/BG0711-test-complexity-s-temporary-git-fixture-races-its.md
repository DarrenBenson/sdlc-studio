# BG0711: test_complexity's temporary git fixture races its own cleanup on CI, reddening main on a teardown rather than a failure

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_complexity.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_complexity_teardown.py, changelog.d/BG0711.md
> **Evidence:** Lint run 35120867337 (push, ccbacc20, 2026-09-16): ci job FAILED (errors=1, skipped=15) with the traceback in test_complexity.py:295 through tempfile's cleanup.
> **Created:** 2026-09-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`CompositeRiskTests.test_assess_finds_churn_for_absolute_path` builds a real git repository inside a `tempfile.TemporaryDirectory` (`test_complexity.py`:291) and lets the context manager remove it. On the GitHub runner the removal raced git's own background work and the suite ERRORED in teardown: `OSError: [Errno 39] Directory not empty: '/tmp/tmp0rbi1y46/.git'`. The assertions had already passed - the run reads FAILED (errors=1) on cleanup alone. It turned main red on ccbacc20, a commit that changed only paperwork and a shipped template, and the pre-push hook then refused the next push until the red was acknowledged, so a teardown race blocks delivery. It is timing-dependent, so it will recur and it will not reproduce on demand.

## Steps to Reproduce

1. Run tools/skill-tests.sh on a CI runner. 2. Occasionally the run ends FAILED (errors=1) with OSError Errno 39 on the temp dir's .git, with every assertion passed. 3. Locally it passes, because nothing else is touching the directory.

## Proposed Fix

Remove the tree with an ignore-errors sweep after the assertions rather than leaving it to the context manager, or stop the repository's background work before cleanup (`git -C <root> gc --auto` is not the only writer; a fresh repo with `core.fsmonitor=false` and no gc removes the class). The test's subject is churn resolution for an absolute path, not directory removal, so its teardown must not be able to fail it.

## Acceptance Criteria

- [ ] **AC1** Given `CompositeRiskTests.test_assess_finds_churn_for_absolute_path` run with the temporary directory's cleanup patched to raise `OSError(39, 'Directory not empty')`, when the test runs under unittest, then it reports success. Fails on: HEAD, whose `tempfile.TemporaryDirectory()` context manager (test_complexity.py:295) raises in teardown and the run reads errors=1
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_complexity_teardown.py::ComplexityTeardownTests::test_a_cleanup_race_does_not_fail_the_churn_test
- [ ] **AC2** Given the same test run with `complexity`'s churn lookup patched to return 0 for the hot file, then it fails. Fails on: a fix that skips the test on CI or wraps its body in a broad except, so its assertion no longer bites
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_complexity_teardown.py::ComplexityTeardownTests::test_the_churn_assertion_still_fails_on_a_miss

## Notes

- Shipped in v6 because the release needs one green CI run on one commit and a rerun costs about 80 minutes. Remove the tree with `shutil.rmtree(..., ignore_errors=True)` after the assertions, or create the repo with no background gc.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-17 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | QA seat: generic AC1 replaced with falsifiable criteria for Sprint 5 |
