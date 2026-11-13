# BG1396: A Verify line with its own -q makes pytest run at -qq with no summary, so a partial skip is stamped pass, and -s and an unpinned _PYTEST_SKIP_NODE add edge cases

> **Status:** Open
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

- [ ] **AC1** Given a Verify line with -q or -s, when a target partly skips or prints a summary-like line, then the verdict is right and `_PYTEST_SKIP_NODE` is exercised. Fails on: a partial skip stamped pass under -q.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py::QuietFlagSkipReadTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
