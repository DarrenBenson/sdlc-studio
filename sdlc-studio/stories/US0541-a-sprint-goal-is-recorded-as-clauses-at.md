# US0541: A Sprint Goal is recorded as clauses at plan time and the close reports a verdict per clause

> **Status:** Ready
> **Delivers:** CR0469
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0185
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator whose sprint goal has more than one clause
**I want** the goal recorded as clauses and a verdict reported per clause
**So that** a goal reached in two parts of three is expressible instead of collapsing to one word

## Acceptance Criteria

### AC1: a goal is recorded as clauses and judged per clause

- **Given** a Sprint Goal recorded as three clauses at plan time
- **When** the close reports its verdict
- **Then** each clause carries its own verdict, so a goal reached in two parts of three is expressible rather than collapsing to one word
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalClauseTests::test_a_three_clause_goal_reports_three_verdicts

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
