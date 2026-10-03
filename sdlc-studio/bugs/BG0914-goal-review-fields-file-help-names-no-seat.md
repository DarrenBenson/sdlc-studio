# BG0914: goal-review --fields-file help names no seat keys, so a fields document keyed role records nothing under the seat

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_review_fields_keys.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T22:02:09Z

## Summary

sprint.py goal-review --fields-file help shows only {"seats": [{...}]}; the flag form documents the positional order role|achievable|..., so an agent writing the document keys each seat 'role', but the code reads s.get('seat') (sprint.py ~3101-3113, ~8396), and the seat name is lost. Seen 2026-10-02 at the goal review: the seats agent had to read the code to find the key.

## Steps to Reproduce

1. Run sprint.py goal-review --help and read the --fields-file entry. 2. Write {"goal": ..., "seats": [{"role": "qa", ...}]} as the flag form's role|achievable order suggests. 3. goal-review record --fields-file it, then show: the seat name is empty.

## Proposed Fix

Name the seat keys the code reads in the --fields-file help text; no new validation or refusal.

## Acceptance Criteria

- [ ] **AC1** Given a goal-review fields document whose seats carry the documented keys, when sprint.py goal-review --help runs, then the --fields-file help names each seat key the code reads (seat, achievable, `done_means`, `one_increment`, note). Fails on: the current help, which names none
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_review_fields_keys.py::GoalReviewFieldsKeysTests::test_help_names_the_seat_keys
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
