# BG1494: test_the_watchdog_sends_sigterm_and_waits_its_grace reads the SIGTERM marker the moment it exists, before the trap has written TERM, and fails CI intermittently

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, changelog.d/BG1494.md
> **Evidence:** GitHub Actions Lint run 43796936774 on 1e2c0445, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T04:15:03Z

## Summary

GitHub Lint run 43796936774 on 1e2c0445 failed at `test_lane_run.LaneDiesWithItsCallerTests.test_the_watchdog_sends_sigterm_and_waits_its_grace` with AssertionError: 'TERM' != ''. The test polls until the marker file exists and then reads it, but the child's SIGTERM trap creates the file before it writes TERM into it, so a read between the two sees an empty file. The test and lanes.py have not changed since 15e3f998 (2026-11-13), and the same test passed on 1787393d, so the red is a race in the test, not a regression.

## Steps to Reproduce

1. Run the test under load on a slow runner.
2. See the marker read empty when the poll wins the race with the trap's write.

## Proposed Fix

Poll until the marker's content is TERM (or the deadline passes), not until the file exists; or have the fake trap write to a temp file and rename it into place.

## Acceptance Criteria

- [ ] **AC1** Given the watchdog test, when the trap creates its marker before writing to it, then the test waits for the written content and passes. Fails on: a read of an empty marker failing the assertion.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py -k watchdog
  - **Verified:** yes (2026-11-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
