# US0545: At plan, the seats are asked whether the chosen content will deliver the goal, and a partial or no answer must name what is missing

> **Status:** Done
> **Delivers:** CR0470
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0186
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator approving a plan
**I want** the seats asked whether the chosen content will deliver the goal, naming anything missing
**So that** the batch is checked against the goal before the work starts, not after

## Acceptance Criteria

### AC1: the plan asks whether the content delivers the goal

- **Given** a resolved batch and a stated goal
- **When** the seats are asked at plan time
- **Then** the question is whether these units deliver this goal, and a partial or no answer that names nothing missing is refused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalContentReviewTests::test_an_unexplained_partial_is_refused
- **Verified:** yes (2026-07-28)

### AC2: the mechanism names its CALLER (BG0385)

- **Caller:** `sprint.cmd_plan` via `sprint plan --content-review` (.claude/skills/sdlc-studio/scripts/sprint.py)
- **Given** the command that should consume this mechanism
- **When** it runs
- **Then** sprint plan --content-review records the plan end of the bookend, and a goal with no answer is reported as UNANSWERED rather than assumed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::InertMechanismsAreReachedTests::test_the_plan_cli_takes_the_content_review
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
| 2026-07-29 | Claude Opus 5 | Amended under BG0385: this unit shipped a mechanism with no caller. The criterion above names the caller and is verified end to end from the command, which is what `caller-check` asks for and what would have refused this unit at delivery. |
