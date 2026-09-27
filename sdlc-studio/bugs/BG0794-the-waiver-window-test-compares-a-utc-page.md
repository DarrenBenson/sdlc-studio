# BG0794: The waiver-window test compares a UTC page date with a local-time waiver date, so it fails for the hour after local midnight in a timezone ahead of UTC

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_waiver_window.py, changelog.d/BG0794.md
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T00:04:38Z

## Summary

`test_lean_waiver_window.py`::WaiverWindowTests::`test_a_waiver_recorded_after_the_page_leaves_it_valid` asserts the waiver row's date equals the page's UTC date. The waiver row is dated in local time, so at 00:58 BST (23:58 UTC) on 2026-09-27 the row read 2026-09-27 and the page 2026-09-26, and the push gate refused. It passed again after UTC midnight. The mismatch may also exist between decisions.py's dating and the report's UTC window, which the fix should check.

## Steps to Reproduce

TZ=Europe/London faketime between 00:00 and 01:00 BST, run the test: '2026-09-26' != '2026-09-27'.

## Proposed Fix

Date waiver rows and the report window in one timezone (UTC), or pin the test's clock; add a case that runs across the local-midnight boundary.

## Acceptance Criteria

- [ ] **AC1** Given the test's clock set to 00:02 UTC, when the page and the waiver are made, then both carry the same UTC date and the test's assertions hold. Fails on: backdating the page five minutes from the wall clock, which crosses UTC midnight for the first five minutes of every day and refused a push at 00:04 UTC
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_waiver_window.py::WaiverWindowTests::test_the_page_and_its_waiver_share_a_day_just_after_utc_midnight

## Notes

- Test-only: pin the clock by injection; decisions.py and the report already date in UTC (the revision row's measured cause). The existing test keeps its assertions.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
| 2026-09-27 | sdlc | Cause measured: the test backdates the page by 5 minutes (generated = now - 5 min) and records the waiver now, so for the first 5 minutes after UTC midnight the two dates differ; it failed at 00:04 UTC and passes after 00:05 UTC. The fix pins the test's clock away from the day boundary |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: one criterion, test-only |
