# BG0921: The goal-review refusal still names a 'role' key after the help names 'seat'

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_review_refusal_keys.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0921.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T00:47:22Z

## Summary

BG0914 made goal-review --fields-file help name the seat keys, but a refusal message (sprint.py ~10741) still tells the writer about 'role', the key confusion the help fix removed.

## Steps to Reproduce

1. goal-review record --fields-file with a malformed seat. 2. The refusal names 'role'.

## Proposed Fix

Name the keys the code reads in the refusal, as the help now does. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a goal-review fields document with a seat missing its key, when record refuses it, then the message names 'seat' and not 'role'. Fails on: the current message
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_review_refusal_keys.py::GoalReviewRefusalKeysTests::test_the_refusal_names_the_seat_key
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
