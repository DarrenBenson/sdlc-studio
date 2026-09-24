# US0888: A lesson that recurs graduates into a check

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py
> **Epic:** EP0261
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** team learning from each sprint
**I want** a lesson that keeps recurring to become a proposed check, and one that never recurs to retire
**So that** learning is measured and acted on without the operator

## Acceptance Criteria

- **AC1:** Given a REJECT whose findings cite a lesson's class code, when the close runs, then that lesson gains a hit for the run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::GraduationTests::test_a_citing_reject_counts_a_hit
- **AC2:** Given a lesson with two hits after it was recorded, when the close runs, then a CR proposing a check or mechanism fix is filed for it and the lesson reads graduating - no operator step
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::GraduationTests::test_two_hits_propose_a_check
- **AC3:** Given a lesson with no hit in its last 5 runs, when the close runs, then it is retired
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::GraduationTests::test_a_quiet_lesson_retires
- **AC4:** Given the report appendix, then it lists each active lesson's hits this run and in total
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::GraduationTests::test_the_report_shows_recurrence

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
