# BG1396: A Verify line with its own -q makes pytest run at -qq with no summary, so a partial skip is stamped pass, and -s and an unpinned _PYTEST_SKIP_NODE add edge cases

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py, .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py, changelog.d/BG1396.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: repair verifyfix, BG1005
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:01Z

## Summary

A pre-existing gap: `-q` in a Verify line takes pytest to `-qq`, which prints no summary, so a partial skip and the all-skipped case are stamped pass. With `-s` a passing test that prints a pytest-style summary line is read as a partial skip and fails, and no test reaches `_PYTEST_SKIP_NODE` (`verify_ac.py`:431), so a mutant stopping it matching survives.

## Steps to Reproduce

Verify line `pytest f.py -q` with one skipped test.

## Proposed Fix

Force a known verbosity and pin the regex.

## Acceptance Criteria

- [ ] **AC1** Given a Verify line `pytest <file> -q` whose target has one passing and one skipped test, and another whose target is entirely skipped, when `verify_ac.py run` runs them, then neither criterion is stamped yes: the first fails naming the skipped test and the second gets the all-skipped verdict.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py::QuietFlagSkipReadTests::test_a_q_on_the_verify_line_still_reads_the_skips
  - **Verified:** yes (2026-11-15)
- [ ] **AC2** Given a Verify line with `-s` whose passing test prints a line shaped like a pytest summary (`1 passed, 1 skipped in 0.01s`), when it runs, then the criterion passes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py::QuietFlagSkipReadTests::test_a_summary_like_line_under_s_is_not_read_as_a_skip
  - **Verified:** yes (2026-11-15)
- [ ] **AC3** Given a run report holding `SKIPPED path::Class::test - reason` lines, when the partial-skip verdict is built, then it names each as `path::Class::test (reason)`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py::QuietFlagSkipReadTests::test_a_skip_node_line_names_its_test
  - **Verified:** yes (2026-11-15)

## Notes

- AC1 must fail on: the tail's -q stacking on the runner's own -q (verify_ac.py:2011), so pytest prints no summary and the skip is stamped pass
- AC2 must fail on: the skip count read as the largest count anywhere in the output (verify_ac.py:482-483) rather than from pytest's own final summary
- AC3 must fail on: `_PYTEST_SKIP_NODE` (verify_ac.py:432) matching nothing, which no test reaches at HEAD
- Still true at HEAD: verify_ac.py:2011 builds `pytest -q -rfEs <tail>`, so a tail -q gives -qq; no test in test_verify_ac_partial_skip.py reaches `_PYTEST_SKIP_NODE`.
- Any verbosity normalisation must agree with the run-identity key, which already folds a `-q` the runner supplies (verify_ac.py:1940-1948 and :4116-4124); the duplicate-selector tests in test_verify_ac.py pin it.
- Builds first in the verify lane; BG1395 follows on the same function.
- End goal 1 (no criterion stamped pass that ran only in part).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed for run fourteen: criteria with Verify lines, notes |
