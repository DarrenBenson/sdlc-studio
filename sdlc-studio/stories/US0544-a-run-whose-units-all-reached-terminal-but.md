# US0544: A run whose units all reached terminal but whose goal was not achieved reports that in the close and the retro, not only the unit count

> **Status:** Draft
> **Delivers:** CR0469
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0185
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: all-terminal units with an unachieved goal is reported as such

- **Given** a run whose units all reached a terminal status but whose goal was not achieved
- **When** the close and the retro report
- **Then** both state the goal was not achieved rather than reporting only the unit count
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::GoalVersusCountTests::test_all_units_terminal_with_an_unachieved_goal_says_so

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
