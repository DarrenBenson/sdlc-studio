# US0887: A lesson is a failure class that counts its repeats

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py
> **Epic:** EP0261
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** team learning from each sprint
**I want** lessons stored as failure classes that count their repeats and reach the work
**So that** a repeated mistake is counted, not re-written as a new lesson, and the rule reaches the agent doing the work

## Acceptance Criteria

- **AC1:** Given the lesson store sdlc-studio/lessons.jsonl, then each row carries id, class, rule, behaviour, inject (plan, build, review), hits and state (active, graduated, retired)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::LessonStoreTests::test_a_lesson_row_carries_its_fields
- **AC2:** Given a retro Try item whose class matches an active lesson, when the close extracts lessons, then a hit naming the run is appended to that lesson and no new lesson is written; a new class writes a new row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::LessonStoreTests::test_a_repeat_is_a_hit_not_a_new_lesson
- **AC3:** Given active lessons, when the plan output, a build brief and a review brief are rendered, then each carries the lessons injected at its phase as rule plus behaviour, at most 5
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::LessonStoreTests::test_lessons_reach_the_phase_they_inject

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
