# US1187: The sprint report of a closed run lists each in-flight amendment with its unit and its reason

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0656
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_amendments.py
> **Epic:** EP0323
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report of a closed run lists each in-flight amendment with its unit and its reason
**So that** CR0656 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each amendment is listed with its unit, what changed and why

- **Given** a closed run whose `batch_changes` holds one Affects amendment and one criterion amendment
- **When** `sprint_report.py` composes the run's page
- **Then** the page lists both, each with its unit id, the paths added or the criterion reworded, and its reason, in the order they were made. Fails on: a report silent about in-flight scope changes, so a reviewer cannot trace an Affects line to a decision
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_amendments.py::SprintReportAmendmentsTests::test_each_amendment_is_listed_with_its_unit_and_reason

### AC2: A run with no amendment composes the page it composed before

- **Given** a closed run whose `batch_changes` holds drops and adds but no amendment, and one holding none at all
- **When** the page is composed
- **Then** it carries no amendments heading and is byte-identical to the page the tree composes today for the same run. Fails on: a filed page whose content, and so whose signed fingerprint, moves when it is re-derived
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_amendments.py::SprintReportAmendmentsTests::test_a_run_without_amendments_composes_an_unchanged_page

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
