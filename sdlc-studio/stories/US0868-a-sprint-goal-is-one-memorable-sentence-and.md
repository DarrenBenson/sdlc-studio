# US0868: A sprint goal is one memorable sentence, and its seat read advises rather than blocks

> **Status:** Draft
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal.py, .claude/skills/sdlc-studio/help/sprint.md
> **Epic:** EP0260
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

- **AC1:** Given a sprint goal of more than 20 words, when sprint plan --write runs, then it refuses with exit 2, names the word count and the 20-word limit, and opens no run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal.py::GoalLengthTests::test_a_goal_over_twenty_words_is_refused
- **AC2:** Given a goal of exactly 20 words, when sprint plan --write runs, then the plan is written - the limit is inclusive, so a gate that refused every goal fails here
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal.py::GoalLengthTests::test_a_twenty_word_goal_plans
- **AC3:** Given an open run whose recorded goal is longer than 20 words, when sprint batch drop or batch add runs, then it is not refused - the limit binds a goal being authored, not a run under way
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal.py::GoalLengthTests::test_an_open_run_with_a_long_goal_can_change_its_batch
- **AC4:** Given a goal whose seat review records an objection, when sprint plan --write runs, then the plan is written with no override flag and the plan output shows the seat's note as advice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal.py::GoalSeatReadTests::test_an_objecting_seat_advises_and_does_not_refuse
- **AC5:** Given a goal with no seat read at all, when the plan is written, then run state records the goal review as not read, never as approved
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal.py::GoalSeatReadTests::test_a_missing_seat_read_is_recorded_as_not_read

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
