# US0604: The close actively REPORTS to the operator - shipped, carried, cost and what the reviews found - rather than leaving a file to be discovered

> **Status:** Done
> **Closed with findings in:** repaired in 5638b18f - the report is emitted from the close's own success path. 307ce91d added a caller the close does not reach, and the line naming it was written by another unit's close commit
> **Delivers:** CR0514
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0198
> **Points:** 5

## User Story

**As a** operator who is told what happened
**I want** the close to report to me actively
**So that** being informed is not the same as a file existing somewhere I might look

## Acceptance Criteria

### AC1: the close reports shipped, carried, cost and findings

- **Given** a completed close
- **When** it finishes
- **Then** it emits a report naming what shipped, what is carried, what it cost and what the reviews found, because a report nobody is told about is the same as no report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseReportReachesTheOperatorTests::test_the_close_prints_the_report_for_a_non_empty_batch
- **Verified:** yes (2026-08-02)

### AC2: an absent figure is named absent, never omitted

- **Given** a close whose cost could not be attributed
- **When** the report renders
- **Then** it states that it could not, rather than dropping the line, because a missing line reads as nothing to report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::CloseReportTests::test_an_absent_figure_is_named_absent
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
