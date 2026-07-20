# US0281: Operator questions are presented as structured decisions with named options and a marked recommendation

> **Status:** Draft
> **Delivers:** CR0369
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/SKILL.md
> **Epic:** EP0092
> **Points:** 3

## User Story

**As a** sprint operator
**I want** questions put to me as structured decisions, not prose
**So that** I can answer quickly and deliberately instead of parsing a narrative

## Acceptance Criteria

### AC1: a question is a decision with named options and consequences

- **Given** the run must ask the operator something
- **When** it asks
- **Then** the surface is the question itself, the named options, and the consequence of each -
  not prose the operator must extract a choice from
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_operator_question_has_named_options_and_consequences

### AC2: the agent's recommendation is marked as such, with the reason

- **Given** the agent has a view on the right answer
- **When** the question is presented
- **Then** its recommended option is marked with the reason, so the operator can accept the
  default quickly or override it deliberately
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_recommendation_is_marked_with_reason

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
