# US0876: sprint close runs once and finishes: gaps become known issues, not refusals

> **Status:** In Progress
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py
> **Epic:** EP0260
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** operator waiting for a sprint to finish
**I want** sprint close to finish in one pass, recording gaps as known issues
**So that** the close never loops through attempt after attempt while nothing changes

## Acceptance Criteria

- **AC1:** Given a run with a goal verdict and a filled retro, when sprint close runs, then in one invocation it files the report, the retro and the handover and exits 0 even with checklist items unanswered, recording each unanswered item in run state key `close_known_issues` instead of refusing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py::OnePassCloseTests::test_close_finishes_in_one_pass_with_gaps_as_known_issues
- **AC2:** Given a gate lane failing inside the close chain, when close runs, then it still finishes and records the lane in `close_known_issues`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py::OnePassCloseTests::test_a_failing_gate_lane_is_a_known_issue_not_a_refusal
- **AC3:** Given a close refused because the goal verdict or the retro is missing, then no close attempt is counted, and `review.max_rounds` no longer caps close attempts
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py::OnePassCloseTests::test_an_early_refusal_is_not_a_counted_attempt
- **AC4:** Given uncommitted changes to tracked batch files, when close runs, then it still refuses naming the files - the one hard refusal kept
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py::OnePassCloseTests::test_a_dirty_tree_still_refuses

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
