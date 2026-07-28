# US0519: A lesson earns a place only by displacing one, and the displaced lesson is named with the reason

> **Status:** Review
> **Delivers:** CR0464
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Epic:** EP0179
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer of a set that must stay small enough to read
**I want** a lesson to earn its place only by displacing one
**So that** the judgement 'is this more important than what is carried' is forced rather than avoided

## Acceptance Criteria

### AC1: adding without displacing is refused

- **Given** a full carried set and a new lesson proposed for it
- **When** the change is recorded
- **Then** it is refused unless a displaced lesson is named, so the size is held by construction rather than by discipline
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::DisplacementTests::test_adding_without_displacing_is_refused
- **Verified:** yes (2026-07-28)

### AC2: the displaced lesson is named with its reason and stays in the registry

- **Given** a displacement
- **When** it is recorded
- **Then** the displaced lesson is named with why it was dropped, and remains in the full registry - displaced is not deleted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::DisplacementTests::test_the_displaced_lesson_is_named_and_retained
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
