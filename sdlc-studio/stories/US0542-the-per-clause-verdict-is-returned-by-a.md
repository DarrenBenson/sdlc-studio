# US0542: The per-clause verdict is returned by a panel of seats, and a panel including the author is refused rather than warned

> **Status:** Draft
> **Delivers:** CR0469
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0185
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the panel returns the verdict and never includes the author

- **Given** a panel of seats judging a goal clause
- **When** the panel is assembled with the unit's author among the seats
- **Then** it is refused rather than warned, and a panel excluding the author returns a per-clause verdict with the evidence it relied on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::GoalPanelTests::test_a_panel_including_the_author_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
