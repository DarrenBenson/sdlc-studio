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

### AC1: the close leaves the operator exactly one account of the run

- **Given** a completed close (PREPARE, under US0832)
- **When** it finishes
- **Then** the operator is left with exactly ONE account naming what shipped, what is carried, what it cost and what the reviews found - the filed report, named on stdout with the command that signs it - because a report nobody is told about is told to nobody, and two accounts derived from two root objects are two chances to disagree
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_the_close_tells_the_operator_where_the_report_is
- **Verified:** yes (2026-09-18)

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
| 2026-09-18 | US0832 delivery | AC1 re-pointed and restated. Its claim was that the close PRINTS the report; US0832 AC5 replaces the two printed accounts (`_draw_report`, `_tell_the_operator`) with one FILED report the close names on stdout. The surviving claim - the operator is left exactly one account - is stronger than the original, and the stamp moves to the test that pins it. |
| 2026-09-18 | delivery | AC1 given its OWN selector. It had been re-pointed at US0832 AC5's test when the class it named was retired, and two criteria sharing one selector cannot both discriminate - a regression in either fails both and neither says which. The claims are genuinely different: AC5 is that there is no SECOND account, this is that the one account REACHES the operator, named with its fingerprint and the command that signs it. |
