# BG0916: A post-close meter stamp other than the report stamp still moves a re-filed page's main-thread tokens

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_meter_any_stamp.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T23:47:03Z

## Summary

BG0913 keeps the first close's window end, but a meter stamp taken after the first close for another reason (a unit moved to In Progress) still moves the re-filed page's main-thread tokens: the reviewer saw 13000 where the first close read 4000.

## Steps to Reproduce

1. Close a run, filing a page. 2. Move a unit In Progress (a meter stamp). 3. Re-close: the page's main-thread tokens move.

## Proposed Fix

Read the main-thread tokens at the first close's report stamp on a re-close, whatever stamps follow it. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a closed run whose page read 4000 main-thread tokens and a later non-report meter stamp, when the run re-closes, then the re-filed page still reads 4000. Fails on: the current code, which reads the later stamp
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_meter_any_stamp.py::RecloseMeterAnyStampTests::test_a_later_stamp_does_not_move_the_meter
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
