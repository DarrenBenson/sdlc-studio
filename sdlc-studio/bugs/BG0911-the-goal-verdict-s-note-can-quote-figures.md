# BG0911: The goal verdict's note can quote figures the filed page contradicts, and the close says nothing

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_note_matches_page.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M3Y7DP close (RPT0015 first filed 2bf8c07d), operator: 'Sounds like a bug'
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T16:45:28Z

## Summary

sprint goal-verdict stores a free-text note recorded before the page is derived. RUN-01M3Y7DP's note quoted tokens 1.87M at 1.46x from a pre-close preview; the filed RPT0015 derived 2.17M at 1.69x (reviewer spend recorded after the preview, and the session meter kept running). The close filed and the check read VALID with the contradiction on the page, so the operator nearly signed a page whose verdict line disagreed with its own Estimates table.

## Steps to Reproduce

1. Record a goal verdict whose note quotes '1.46x'. 2. Record more delegated spend. 3. sprint close -> the page's Tokens ratio reads 1.69x beside a verdict note saying 1.46x, with no warning.

## Proposed Fix

At the close, compare each ratio and token figure the note quotes with the page's derived Estimates and print one line naming any that differ, so the note is corrected before the page is filed (a warning, not a refusal).

## Acceptance Criteria

- [ ] **AC1** Given a goal verdict note quoting a tokens ratio of 1.46x and a page that derives 1.69x, when sprint close files the page, then it prints one line naming the note's 1.46x and the page's 1.69x, and the exit code is unchanged. Fails on: the current close prints nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_note_matches_page.py::GoalNoteMatchesPageTests::test_a_note_figure_the_page_contradicts_is_named
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
