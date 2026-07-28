# US0546: At close, the seats are asked whether the delivered content achieved the goal, with the undelivered units and the defects raised supplied rather than recalled

> **Status:** Draft
> **Delivers:** CR0470
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0186
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the close asks the mirrored question with the evidence supplied

- **Given** a closed batch with undelivered units and defects raised against delivered ones
- **When** the seats are asked at close
- **Then** the question carries those units and defects with it rather than relying on recall
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalContentReviewTests::test_the_close_question_supplies_the_shortfall

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
