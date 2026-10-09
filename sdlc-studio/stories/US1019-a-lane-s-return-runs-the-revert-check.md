# US1019: A lane's return runs the revert check, so the builder learns its tests cannot fail before a reviewer does

> **Status:** Draft
> **Delivers:** CR0624
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_return_revert_check.py, changelog.d/US1019.md
> **Epic:** EP0281
> **Points:** 3
> **Depends on:** BG1014, US1017, US1020
> **Persona:** Maya Okafor

## User Story

**As** a team lead whose reviewers spend rounds breaking code by hand to see whether the tests notice
**I want** `sprint lane return` to run the revert check when a unit's criteria are green and no other lane is in flight, and to block the return when none of the criteria goes red
**So that** the builder fixes a test that cannot fail before the review, and the review round is spent on the code

## Acceptance Criteria

- **AC1:** Given an open run with no other lane in flight, whose batch unit has criteria that pass but all stay green with its production change reverted to the run's base, when `sprint.py lane return --units <id>` runs, then it exits 1 as blocked, naming each green criterion and `verify_ac.py revert-check`, and the production file is byte-identical afterwards.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_return_revert_check.py::LaneReturnRevertCheckTests::test_lane_return_blocks_a_unit_whose_criteria_pass_without_the_change
- **AC2:** Given a batch unit with one criterion that goes red and one that stays green after the revert, when `sprint.py lane return` runs, then it returns fixed and names the green criterion as passing without the change.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_return_revert_check.py::LaneReturnRevertCheckTests::test_lane_return_names_a_green_criterion_and_returns_fixed
- **AC3:** Given a batch unit whose Affects names no production file, when `sprint.py lane return` runs, then it returns fixed and says that revert-check could not judge it, and why.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_return_revert_check.py::LaneReturnRevertCheckTests::test_lane_return_reports_a_unit_it_cannot_judge_without_blocking
- **AC4:** Given an open run in which another batch unit's lane was briefed and has not returned, when `sprint.py lane return --units <id>` runs for a unit the check would block, then it returns without blocking, reports the unit as not judged and names the lane still in flight, and no production byte, mtime or verifier marker changes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_return_revert_check.py::LaneReturnRevertCheckTests::test_no_revert_while_another_lane_is_in_flight

## Notes

- Release: later (D0355 breakdown G7, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: `cmd_lane` return never calls `revert_check`
- AC2 must fail on: block the return on any criterion that stays green
- AC3 must fail on: read a not-judged revert as blocking in the lane's verdict
- AC4 must fail on: revert while another lane is in flight, which is the CR0552 hazard of a parallel lane's tests reading the base bytes
- In a sprint, units reach Done or Fixed only at `sprint sign` (sprint.py:6180-6186), after review. The close's terminal-gate hold shows a refusal first, but that is also after review. CR0624's Impact (a review round spent finding this) is answered only here.
- The check runs only when `lane_verify` reports every criterion green, since a red criterion already blocks. It also runs only when `run_state.lanes_in_flight` (read as `_lanes_never_returned` does, sprint.py:6100) names no other unit. The window (BG1014) only scopes what a commit may stage (reference-sprint.md:475-481), so a parallel lane's tests could still read the reverted file. The close and the sign still judge a unit skipped here.
- It uses the run's base and holds BG1014's window for the duration of the revert.
- The verdict is not cached for the close or the sign (D0180).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G7 after the refine panel's review |
