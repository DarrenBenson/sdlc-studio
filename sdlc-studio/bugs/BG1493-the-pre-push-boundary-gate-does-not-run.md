# BG1493: The pre-push boundary gate does not run CI's green-run noise gate, so a push that passes locally turns GitHub Lint red

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** tools/run-suite.sh, .githooks/pre-push, tools/tests/test_run_suite.py, changelog.d/BG1493.md
> **Evidence:** GitHub Actions Lint on 7c64bf26, 2026-11-16 00:00 UTC; BG1489.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T01:57:44Z

## Summary

Run thirteen's US1061/US1062 added a warning that passing tests leaked. The pre-push boundary gate on the gate host passed 7c64bf26, but GitHub's Lint workflow failed on it: tools/skill-tests.sh's green-run noise gate counted 112 diagnostic lines against `_total` 104 (BG1489). The push gate is documented as the full-suite check, yet one CI lane it does not run judged main red after the push. D0181 reads a red main before the next push, and that costs a fix cycle every time.

## Steps to Reproduce

1. Add a test that prints a warning while passing.
2. Push: the pre-push gate passes.
3. GitHub Lint fails on test-noise.

## Proposed Fix

Have the boundary push suite run the skill suite through tools/skill-tests.sh's noise gate (or apply tools/`test_noise.py` to the suite output it already captures) so a leak above the budget refuses the push.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run thirteen's US1061/US1062 added a warning that passing tests leaked.
- [ ] **AC2** The proposed fix lands, pinned by a test: Have the boundary push suite run the skill suite through tools/skill-tests.sh's noise gate (or apply tools/`test_noise.py` to the suite output it already...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
