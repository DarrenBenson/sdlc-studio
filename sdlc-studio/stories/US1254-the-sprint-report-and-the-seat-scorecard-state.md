# US1254: The sprint report and the seat scorecard state escapes per 100 points delivered, from the linked records

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0706
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_report_escapes_per_100.py, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, changelog.d/US1254.md
> **Epic:** EP0346
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report and the seat scorecard state escapes per 100 points delivered, from the linked records
**So that** CR0706 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The report states escapes per 100 points with both counts

- **Given** a closed run that delivered 40 points, and two bugs recorded `Escaped: yes` in the window `retro.py seats` charges later bugs over, beside one bug in that window that did not escape
- **When** `sprint_report.py` builds the run's report
- **Then** it states 5.0 escapes per 100 points delivered, beside the 2 escaped bugs and the 40 points it was computed from, each escaped bug named by id. Fails on: the bug that did not escape counted, an escaped bug outside the window counted, or a rate with no counts to recompute it from
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_escapes_per_100.py::EscapesPer100Tests::test_the_report_states_the_rate_with_its_counts

### AC2: A run that delivered no points states NOT MEASURED

- **Given** a closed run that delivered no points, and separately a run that delivered points with no escaped bug in its window
- **When** each report is built
- **Then** the first states the rate as NOT MEASURED with the reason, and the second states 0.0 over its points. Fails on: a division error, or zero shown where nothing could be measured
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_escapes_per_100.py::EscapesPer100Tests::test_no_points_is_not_measured_and_no_escapes_is_zero

### AC3: The seat scorecard states each seat's escapes per 100 points it approved

- **Given** a retro whose qa seat approved units totalling 20 points, one of them named by an escaped bug's `Escaped-via`, and whose engineering seat approved 20 points with no escape charged
- **When** `retro.py seats --id <retro>` is printed as text and as JSON
- **Then** the qa seat states 5.0 escapes per 100 points approved, from 1 escape over 20 points, and the engineering seat 0.0 over 20; the JSON carries the same three figures per seat. Fails on: an escape charged to a seat that did not approve the unit, or a rate computed over the run's points in place of the seat's own
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_escapes_per_100.py::EscapesPer100Tests::test_each_seat_states_its_escapes_per_100_points_approved

### AC4: The annex catalogues the report's new figure

- **Given** the filed page and `reference-evidence-schema.md`
- **When** the page's figure keys are read against the annex
- **Then** the annex lists the escapes figure, its unit and its source, and the annex's minor version is raised. Fails on: a figure the page carries and the annex does not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_escapes_per_100.py::EscapesPer100Tests::test_the_annex_catalogues_the_escapes_figure

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
