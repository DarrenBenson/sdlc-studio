# US0543: An open defect is judged against the goal clauses: one that falsifies a clause blocks the close, one that does not is recorded leavable with its priority

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

**As a** an operator deciding whether a defect can wait
**I want** each open defect judged against the goal clauses
**So that** the decision rests on whether it falsifies the goal rather than on a severity somebody guessed

## Acceptance Criteria

### AC1: an open defect is judged against the clauses

- **Given** an open defect and a goal recorded as clauses
- **When** the close judges the defect
- **Then** one falsifying a clause blocks the close, and one that does not is recorded leavable with its priority and the clause reasoning
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DefectAgainstGoalTests::test_a_clause_falsifying_defect_blocks_and_others_are_recorded_leavable

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
