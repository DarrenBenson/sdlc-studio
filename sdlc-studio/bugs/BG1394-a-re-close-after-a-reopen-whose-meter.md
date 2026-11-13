# BG1394: A re-close after a reopen whose meter cannot be read drops the first window, takes no reading and says nothing on the page

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_re_close_unreadable_meter.py, changelog.d/BG1394.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: repair costfix, BG1279
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:10:44Z

## Summary

After `sprint reopen`, a second close whose meter is unreadable loses the first close's window and records no reading, with no sign on the report page.

## Steps to Reproduce

Close, reopen, make the meter unreadable, close again.

## Proposed Fix

Keep the earlier window and write the gap on the page.

## Acceptance Criteria

- [ ] **AC1** Given a reopened run whose meter cannot be read at the second close, when the close runs, then the first window is kept and the page says the second reading is missing. Fails on: the window dropped silently.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_re_close_unreadable_meter.py::ReCloseUnreadableMeterTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
