# US0569: the sprint report is DERIVED from the tree: planned against delivered, and scope creep as a number

> **Status:** Done
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0192
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator judging whether a sprint is closeable
**I want** the report's figures read out of the tree rather than typed in, with scope creep as a number
**So that** a report I can trust is a report nobody could have filled in from memory

## Acceptance Criteria

### AC1: PLANNED and DELIVERED are both derived, and both are on the page

- **Given** a closed run whose approved batch was mutated by drops and adds during the run
- **When** the sprint report is composed
- **Then** the planned units and points are reconstructed from the run's own batch-change ledger and reported beside the delivered figures, so commitment against actual can be read without arithmetic - a report that states only what shipped cannot answer the first question anyone asks of a sprint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistDerivedFiguresTests::test_planned_and_delivered_are_both_derived_and_reported
- **Verified:** yes (2026-07-30)

### AC2: scope creep is a NUMBER against the plan, not a list to read

- **Given** a run planned with N units, during which artefacts were filed that the plan never named
- **When** the report is composed
- **Then** it states the count of unplanned artefacts and the ratio against planned units on one line, because the ratio is the signal - 17 filed against 11 planned is the fact an operator needs and a list of 17 titles is not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistDerivedFiguresTests::test_scope_creep_is_reported_as_a_count_and_a_ratio
- **Verified:** yes (2026-07-30)

### AC3: a figure the tree cannot answer is UNKNOWN, never blank and never invented

- **Given** a run whose points are unreadable on one unit and whose batch line names no ids
- **When** the report is composed
- **Then** each unanswerable figure is marked unknown with the reason, rather than rendered as zero or omitted - zero and unreadable call for opposite responses, and picking the tidier one is how a sprint that shipped nothing and a retro nobody filled in came to read the same
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistDerivedFiguresTests::test_an_unanswerable_figure_is_unknown_not_zero
- **Verified:** yes (2026-07-30)

### AC4: the report and the checklist are ONE artefact

- **Given** the compulsory checklist for a sprint
- **When** the report is composed
- **Then** every compulsory item appears as a row of the report itself, so there is no second document to keep in step - two close-time documents that both claim to record the run is the drift this repo keeps filing bugs about
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistDerivedFiguresTests::test_every_compulsory_item_is_a_row_of_the_report
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
