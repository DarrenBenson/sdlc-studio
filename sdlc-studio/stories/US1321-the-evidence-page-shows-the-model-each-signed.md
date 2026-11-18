# US1321: The evidence page shows the model each signed run used, regenerated through RPT0035

> **Status:** Done
> **Risk-class:** elevated
> **Delivers:** CR0742
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py, docs/evidence.md, tools/tests/test_evidence_page_committed.py, changelog.d/US1321.md
> **Epic:** EP0377
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The evidence page shows the model each signed run used, regenerated through RPT0035
**So that** CR0742 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each evidence row names the model its report priced

- **Given** signed reports whose JSON records the models they priced, and one that records none
- **When** `sprint_report.py evidence` writes the table
- **Then** each row has a Model column naming the models its report priced, and "not recorded" for a report that records none. Fails on: a model the report does not carry, or a blank cell
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_each_row_names_the_model_its_report_priced
- **Verified:** yes (2026-11-18)

### AC2: The committed page is regenerated through RPT0035

- **Given** `docs/evidence.md`
- **When** the committed-page check re-derives it from the signed reports
- **Then** it matches, its newest report is RPT0035, and it says the reports do not record the harness, naming the CR that adds it. Fails on: a stale page, or the harness gap unstated
- **Verify:** pytest tools/tests/test_evidence_page_committed.py
- **Verified:** yes (2026-11-18)

## Notes

- The reports record no harness field (checked on RPT0035): CR0743 adds it; this story shows the model only and names CR0743 on the page.
- Do not touch the report's Estimates table (CR0741 owns that change).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Created via `new` (deterministic) |
