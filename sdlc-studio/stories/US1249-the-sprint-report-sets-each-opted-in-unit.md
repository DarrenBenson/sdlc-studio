# US1249: The sprint report sets each opted-in unit against comparable units, so the keep-or-drop rule can be judged

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0701
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_ownership_trial.py, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, changelog.d/US1249.md
> **Epic:** EP0343
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report sets each opted-in unit against comparable units, so the keep-or-drop rule can be judged
**So that** CR0701 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each opted-in unit is set against the same-size units of its run

- **Given** a closed run that delivered one opted-in unit of 3 points, two 3-point units that did not opt in and one 5-point unit
- **When** `sprint_report.py` builds the run's report
- **Then** the ownership trial section has a row for the opted-in unit and one for the two 3-point units together, each stating priced tokens per point, review rounds, blocking findings that cite a file outside the unit's Affects, and duplicated lines removed where the unit's record states it; the 5-point unit is in neither. Fails on: a comparison against a unit of another size, or a figure shown as zero where it was not measured
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_ownership_trial.py::OwnershipTrialReportTests::test_an_opted_in_unit_is_set_against_same_size_units

### AC2: An opted-in unit with no same-size comparator says so

- **Given** a closed run whose only opted-in unit is the one unit of its size
- **When** the report is built
- **Then** the unit's row states its own figures and says the run holds no comparable unit of that size. Fails on: the unit dropped from the section, or compared with the nearest size
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_ownership_trial.py::OwnershipTrialReportTests::test_no_same_size_comparator_is_stated

### AC3: A run with no opted-in unit carries no trial section, and the annex says so

- **Given** a closed run in which no unit opts in, and `reference-evidence-schema.md`
- **When** the report is built and its sections are read against the annex
- **Then** the page carries no ownership trial section, the annex catalogues the section as conditional with that as its absent-when, with every row key it carries, and the annex's minor version is raised. Fails on: an empty section on every report, or a section the annex does not catalogue
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_ownership_trial.py::OwnershipTrialReportTests::test_the_section_is_absent_without_an_opted_in_unit_and_catalogued

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
