# BG0794: The waiver-window test compares a UTC page date with a local-time waiver date, so it fails for the hour after local midnight in a timezone ahead of UTC

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_waiver_window.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
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

- [ ] **AC1** The behaviour described is corrected: `test_lean_waiver_window.py`::WaiverWindowTests::`test_a_waiver_recorded_after_the_page_leaves_it_valid` asserts the waiver row's date equals the page's UTC...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: TZ=Europe/London faketime between 00:00 and 01:00 BST, run the test: '2026-09-26' != '2026-09-27'.
- [ ] **AC3** The proposed fix lands, pinned by a test: Date waiver rows and the report window in one timezone (UTC), or pin the test's clock; add a case that runs across the local-midnight boundary.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
| 2026-09-27 | sdlc | Cause measured: the test backdates the page by 5 minutes (generated = now - 5 min) and records the waiver now, so for the first 5 minutes after UTC midnight the two dates differ; it failed at 00:04 UTC and passes after 00:05 UTC. The fix pins the test's clock away from the day boundary |
