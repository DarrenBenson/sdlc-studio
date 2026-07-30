# US0569: the sprint report is DERIVED from the tree: planned against delivered, and scope creep as a number

> **Status:** Draft
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Epic:** EP0192
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator judging whether a sprint is closeable
**I want** the report's figures read out of the tree rather than typed in, with scope creep as a number
**So that** a report I can trust is a report nobody could have filled in from memory

## Acceptance Criteria

### AC1: the delivered figures are DERIVED, never typed in

- **Given** a closed run whose batch holds units at several statuses, with points on each
- **When** the sprint report is generated
- **Then** the delivered points, the unit count and the per-status split are read from the tree, and a figure the tree cannot answer is marked UNKNOWN rather than left blank or invented - a report an agent fills in by hand records what the agent remembers, which is the failure the derived index exists to prevent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::SprintReportTests::test_the_delivered_figures_are_derived_from_the_tree

### AC2: scope creep is a NUMBER against the plan, not a list to read

- **Given** a run planned with N units, during which artefacts were filed that the plan never named
- **When** the report is generated
- **Then** it states the count of unplanned artefacts and the ratio against planned units on one line, because the ratio is the signal - 17 filed against 11 planned is the fact an operator needs and a list of 17 titles is not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::SprintReportTests::test_scope_creep_is_reported_as_a_number_and_a_ratio

### AC3: the report and the checklist are ONE artefact

- **Given** the compulsory checklist for a sprint
- **When** the report is generated
- **Then** every compulsory item appears as a section of the report itself, so there is no second document to keep in step - two close-time documents that both claim to record the run is the drift this repo keeps filing bugs about
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::SprintReportTests::test_every_compulsory_item_is_a_section_of_the_report

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
