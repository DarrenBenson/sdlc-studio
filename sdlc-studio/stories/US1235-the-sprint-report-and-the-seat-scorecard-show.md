# US1235: The sprint report and the seat scorecard show the release change failure rate, naming its source records

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0695
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py
> **Epic:** EP0339
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report and the seat scorecard show the release change failure rate, naming its source records
**So that** CR0695 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The sprint report shows the release change failure rate with its sources

- **Given** a project with settled release records and a linked incident, and a closed run
- **When** the sprint report is rendered through `sprint_report.py`
- **Then** it carries the release change failure rate on its own row, citing the release records and incident issues it was derived from, beside the escapes figure where the report carries one, and the CI-run rate of the DORA table is still present and unchanged. Fails on: the release figure replacing or merged into the CI-run rate, or a figure with no source cited
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py::ReportChangeFailureRateTests::test_the_report_shows_the_release_rate_with_its_source_records

### AC2: The seat scorecard shows the same figure

- **Given** the same project
- **When** `retro.py seats` is run
- **Then** the scorecard states the release change failure rate with its source records, and the value and the releases counted are the ones the `escape.py` command prints for the same window. Fails on: a second calculation that can disagree with the command
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py::ReportChangeFailureRateTests::test_the_seat_scorecard_shows_the_figure_the_command_derives

### AC3: Not measured and pending carry through to the report

- **Given** a project with no release record, and one whose only release is inside the settling period
- **When** the sprint report is rendered in each
- **Then** the row reads NOT MEASURED with the command's reason in the first and names the release as pending in the second, never 0% and never an empty cell, and the report template carries the row. Fails on: 0% or a blank where nothing was measured
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py::ReportChangeFailureRateTests::test_not_measured_and_pending_reach_the_report

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
