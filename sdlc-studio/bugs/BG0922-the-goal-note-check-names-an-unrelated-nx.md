# BG0922: The goal-note check names an unrelated 'Nx' figure as a contradiction and misses 1.7X and the multiplication sign

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_note_ratio_spelling.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0922.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T00:47:24Z

## Summary

BG0911's note check reads any 'Nx' token as a ratio, so a note saying '10x faster' is named as contradicting the page, and it ignores a ratio written 1.7X or with the multiplication sign (sprint.py ~9355).

## Steps to Reproduce

1. A goal verdict note saying '10x faster' and quoting the page's ratio. 2. sprint close names 10x as a contradiction. 3. A note quoting the wrong ratio as 1.4X is not named.

## Proposed Fix

Read only ratios that sit beside a ratio's measure name, and accept X and the multiplication sign. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a note saying '10x faster' that quotes the page's tokens ratio, and a second note quoting a wrong ratio as 1.4X, when sprint close files the page, then the first names nothing and the second is named. Fails on: the current parser
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_note_ratio_spelling.py::GoalNoteRatioSpellingTests::test_only_measure_ratios_are_read
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
