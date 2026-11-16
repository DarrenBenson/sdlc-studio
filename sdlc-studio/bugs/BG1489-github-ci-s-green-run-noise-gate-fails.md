# BG1489: GitHub CI's green-run noise gate fails on main: critic record's new author-form warning leaks from passing tests, 112 diagnostic lines against a baseline of 104

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_under_depth.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_bug_close_review.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_optional.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_errors.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_rebrief.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_verdict_integrity.py, changelog.d/BG1489.md
> **Evidence:** GitHub Actions Lint run on 7c64bf26, 2026-11-16 00:00 UTC: test-noise 112 > 104.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T00:36:21Z

## Summary

The Lint workflow on 7c64bf26 failed at 'Run the unit suites once ... with the green-run noise gate': tools/`test_noise.py` counted 112 diagnostic lines printed by a PASSING run against the recorded full-run total of 104 in tools/test-noise-baseline.json. The new lines include `WARNING: author '<name>' lacks the <holder> (<role>) form ...`, printed by critic.py record (critic.py near 2657, added by US1061/US1062 in 01e3aa92, run thirteen) from tests that record a verdict with a bare author such as 'the author', 'grace' or 'dev' without capturing stderr. The local push gate does not run the noise gate, so main went red on CI only. The last green Lint was 1787393d.

## Steps to Reproduce

1. Read the failed Lint run for 7c64bf26 (gh run view --log-failed).
2. See test-noise: a PASSING run printed 112 diagnostic line(s), above 104.

## Proposed Fix

In each test that records a verdict with a bare author, capture stderr (`contextlib.redirect_stderr` or the CLI's captured output) and assert the warning where it is the point, so a green run prints no new line; never raise the baseline. Measure with tools/`test_noise.py` against tools/test-noise-baseline.json for the modules changed.

## Acceptance Criteria

- [ ] **AC1** Given the skill test suite at HEAD, when it runs green under tools/skill-tests.sh's noise gate, then it prints no more diagnostic lines than tools/test-noise-baseline.json records, with the baseline unchanged or lowered. Fails on: any author-form warning reaching the console from a passing test.
  - **Verify:** bash tools/skill-tests.sh test_critic.py test_critic_under_depth.py test_lean_bug_close_review.py test_lean_brief_optional.py test_lean_lock_errors.py test_lean_no_plan_phase.py test_lean_rebrief.py test_lean_verdict_integrity.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
