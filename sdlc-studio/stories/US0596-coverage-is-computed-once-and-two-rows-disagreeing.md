# US0596: Coverage is computed once, and two rows disagreeing about it is itself an outstanding item

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0197
> **Points:** 3

## User Story

**As a** operator reading one report
**I want** coverage computed once
**So that** a close cannot report three different answers to one question

## Acceptance Criteria

### AC1: coverage has one computation

- **Given** the close chain, the checklist coverage row and the review row
- **When** a close composes its report
- **Then** all three read one computed value, so a run cannot report `9/9 covered`, `0 covered, 37 uncovered` and `71 recorded passes` about the same question
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::CoverageConsistencyTests::test_coverage_has_one_source

### AC2: a disagreement is itself outstanding

- **Given** a report in which two coverage readings differ
- **When** the checklist resolves
- **Then** the disagreement is an OUTSTANDING item naming both readings, because a report contradicting itself is a fact about the report that nothing currently notices
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::CoverageConsistencyTests::test_a_disagreement_is_outstanding

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
