# US1242: The sprint report states reviews, upheld rejections and traced escapes for each reviewer model family

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0698
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_reviewer_family.py, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, changelog.d/US1242.md
> **Epic:** EP0341
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report states reviews, upheld rejections and traced escapes for each reviewer model family
**So that** CR0698 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The report counts reviews, upheld rejections and escapes for each family

- **Given** a closed run whose delivery ledger holds verdicts by reviewers of two model families, one REJECT among them later superseded as recorded in error, and an escaped bug charged to one family's approval by the rule `retro.py seats` charges a missed bug
- **When** `sprint_report.py` builds the run's report
- **Then** its reviewer-family section has one row per family stating the reviews done, the rejections upheld (a REJECT not superseded as recorded in error) and the escapes traced to that family's approvals. Fails on: the superseded REJECT counted as upheld, the escape charged to the other family, or one total for all reviewers
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_reviewer_family.py::ReviewerFamilyReportTests::test_each_family_states_reviews_upheld_rejections_and_escapes

### AC2: Verdicts naming no model are a row of their own

- **Given** the same run with rows recorded before the reviewer's model was stated
- **When** the report is built
- **Then** those rows are counted under `unknown`, and the families' review counts sum to the run's delivery verdict rows. Fails on: rows with no model dropped from the table, or folded into a named family
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_reviewer_family.py::ReviewerFamilyReportTests::test_rows_with_no_model_are_counted_as_unknown

### AC3: The annex catalogues the section the builder emits

- **Given** the filed page and `reference-evidence-schema.md`
- **When** the page's sections and row keys are read against the annex tables
- **Then** the annex lists the section, its placement, when it is emitted and every row key it carries, and the annex's minor version is raised. Fails on: a section or row key the page carries and the annex does not, or an unchanged annex version
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_reviewer_family.py::ReviewerFamilyReportTests::test_the_annex_catalogues_the_reviewer_family_section

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
