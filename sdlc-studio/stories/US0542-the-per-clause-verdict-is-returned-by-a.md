# US0542: The per-clause verdict is returned by a panel of seats, and a panel including the author is refused rather than warned

> **Status:** Done
> **Delivers:** CR0469
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0185
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator relying on an independent judgement
**I want** the per-clause verdict returned by a panel that refuses to include the author
**So that** the verdict is not the author marking their own homework

## Acceptance Criteria

### AC1: the panel returns the verdict and never includes the author

- **Given** a panel of seats judging a goal clause
- **When** the panel is assembled with the unit's author among the seats
- **Then** it is refused rather than warned, and a panel excluding the author returns a per-clause verdict with the evidence it relied on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::GoalPanelTests::test_a_panel_including_the_author_is_refused
- **Verified:** yes (2026-07-28)

### AC2: the mechanism names its CALLER (BG0385)

- **Caller:** `sprint.close_goal_judgement`, reached from `sprint close` (.claude/skills/sdlc-studio/scripts/sprint.py)
- **Given** the command that should consume this mechanism
- **When** it runs
- **Then** sprint close calls goal_panel over the Sprint Goal's clauses and prints the per-clause verdict, with the authoring session excluded from the panel
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::InertMechanismsAreReachedTests::test_the_close_reaches_the_goal_panel_and_reports_per_clause
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
| 2026-07-29 | Claude Opus 5 | Amended under BG0385: this unit shipped a mechanism with no caller. The criterion above names the caller and is verified end to end from the command, which is what `caller-check` asks for and what would have refused this unit at delivery. |
