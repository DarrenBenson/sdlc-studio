# US1282: The sprint report carries the same two machinery shares as the plan printed

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0722
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0360
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report carries the same two machinery shares as the plan printed
**So that** CR0722 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The report carries the two shares the plan printed

- **Given** a run planned over a batch whose units carry `Area` tags and `Affects`, then closed
- **When** the sprint report is drawn for the run
- **Then** the report states points by area from the tags and from the path map, with the same figures per area and the same named disagreeing units as the plan printed for that batch. Fails on: a report with no share, a single share, or figures computed by a second implementation that drift from the plan's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::MachineryShareReportTests::test_the_report_states_the_same_two_shares_as_the_plan

### AC2: The report states the maintenance declaration, or its absence over the cap

- **Given** one closed run over one third machinery with a recorded maintenance declaration, and one over the cap with none
- **When** the sprint report is drawn for each
- **Then** the first report states the declaration and its reason, and the second states that the run was over the cap by the named reading with no declaration recorded. Fails on: a report that reads the same for a declared maintenance run and an undeclared one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::MachineryShareReportTests::test_the_report_states_the_declaration_or_its_absence

### AC3: A run whose units carry no area tags is reported as untagged

- **Given** a closed run whose units predate the `Area` field
- **When** the sprint report is drawn
- **Then** the by-tag reading says the units are untagged and gives no machinery percentage for it, the by-path reading is still stated, and the report is drawn without error. Fails on: an older run reported as zero machinery by tag, or a report that fails to draw for it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::MachineryShareReportTests::test_an_untagged_run_is_reported_untagged_not_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
