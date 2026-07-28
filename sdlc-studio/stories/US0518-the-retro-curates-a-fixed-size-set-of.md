# US0518: The retro curates a fixed-size set of carried lessons, and the content check requires it

> **Status:** Review
> **Delivers:** CR0464
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Epic:** EP0179
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** agent starting a sprint with 252 lessons behind me
**I want** the retro to curate a fixed-size set of the lessons that matter for the next batch
**So that** what I carry is a judgement someone made, not a ranking I will skim

## Acceptance Criteria

### AC1: the retro's content check requires a curated set

- **Given** a retro with no carried-lessons section
- **When** its content check runs
- **Then** it fails, naming the missing curation, so the set cannot quietly stop being maintained
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::CarriedLessonsTests::test_a_retro_without_a_curated_set_fails
- **Verified:** yes (2026-07-28)

### AC2: the set is fixed size and a retro exceeding it is refused

- **Given** a retro carrying more than the configured number
- **When** the check runs
- **Then** it is refused, because a set that can grow is the 252-entry summary again
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::CarriedLessonsTests::test_an_oversized_carried_set_is_refused
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
