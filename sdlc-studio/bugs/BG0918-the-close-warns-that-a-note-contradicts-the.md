# BG0918: The close warns that a note contradicts the page when the note writes 1.70x and the page 1.7x

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_note_ratio_numeric.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T23:47:06Z

## Summary

BG0911 compares the note's ratio with the page's as text, so the same ratio written 1.70x and 1.7x is named as a contradiction.

## Steps to Reproduce

1. A goal verdict note quoting 1.70x. 2. A page deriving 1.7x. 3. sprint close names a contradiction.

## Proposed Fix

Compare the ratios as numbers at the page's precision. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a note quoting 1.70x and a page deriving 1.7x, when sprint close files the page, then no contradiction is named, and a note quoting 1.46x is still named. Fails on: the current text comparison
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_note_ratio_numeric.py::GoalNoteRatioNumericTests::test_equal_ratios_written_differently_agree

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
