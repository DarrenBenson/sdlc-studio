# US0877: The retro is three lines, and a re-run close keeps one report per run

> **Status:** In Progress
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/reviews/retro.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_retro.py
> **Epic:** EP0260
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** team learning from each sprint
**I want** a three-line retro whose Try items become lessons exactly once, and one report per run
**So that** the retro is quick to write and the record is not cluttered with duplicates

## Acceptance Criteria

- **AC1:** Given a retro scaffold, then its sections to fill are Keep, Stop and Try and nothing else is required
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro.py::ThreeLineRetroTests::test_the_retro_scaffold_is_keep_stop_try
- **AC2:** Given a retro with an entry in each of Keep, Stop and Try, when retro validate runs, then it passes; with more than 3 Try items it fails naming the limit; with placeholder text left in it fails
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro.py::ThreeLineRetroTests::test_validate_accepts_three_lines_and_rejects_placeholders_and_long_try
- **AC3:** Given a retro's Try items, when the close extracts lessons, then each Try item is recorded once as a lesson, and running the extraction again records none twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro.py::ThreeLineRetroTests::test_try_items_become_lessons_exactly_once
- **AC4:** Given run R's report already filed as RPTn, when the report is filed again for R, then RPTn is rewritten in place and no new id is allocated; a different run gets a new id
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retro.py::OneReportPerRunTests::test_refiling_a_runs_report_reuses_its_id

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
