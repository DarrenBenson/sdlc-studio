# US0521: A lesson violated again after being carried is reported at the close, naming the unit that repeated it

> **Status:** Review
> **Delivers:** CR0464
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Epic:** EP0179
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator deciding whether a lesson needs a guard rather than a louder note
**I want** a lesson violated again after being carried reported at the close, naming the unit
**So that** a repeat is visible as evidence rather than being absorbed into the next retro

## Acceptance Criteria

### AC1: a repeat after carrying is reported at the close with the unit named

- **Given** a lesson in the carried set and a unit in the batch that violated it
- **When** the close runs
- **Then** the repeat is reported, naming the lesson and the unit, so the evidence is attached to the work that produced it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RepeatTests::test_a_repeat_after_carrying_is_reported_with_its_unit
- **Verified:** yes (2026-07-28)

### AC2: a lesson that was not carried is not counted as a repeat

- **Given** a violation of a lesson outside the carried set
- **When** the close runs
- **Then** it is not reported as a repeat, because the claim is about what was carried and read, not about the whole registry
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RepeatTests::test_an_uncarried_lesson_is_not_a_repeat
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
