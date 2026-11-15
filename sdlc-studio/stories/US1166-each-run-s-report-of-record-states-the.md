# US1166: Each run's report of record states the effort each builder and reviewer was dispatched at, read from the run record

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0699
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py, changelog.d/US1166.md
> **Epic:** EP0311
> **Points:** 3
> **Depends on:** US1165, US1160, US1161
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** each run's report of record states the effort each builder and reviewer was dispatched at, read from the run record
**So that** I know what each team's delivery costs per point and can hold it to a monthly budget

## Acceptance Criteria

- **AC1:** Given a run record whose plan stamped builder low and reviewer medium on its units, when `sprint_report.py build` composes the report of record and it is rendered, then the cost section carries an effort figure per role sourced from the run record, and the page shows it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortTests::test_the_report_states_each_roles_effort_from_the_run_record
  - **Verified:** yes (2026-11-15)
- **AC2:** Given a run record planned before the setting existed (no effort stamped), when the report is built, then the effort figure reads NOT MEASURED with its reason, never inherit and never blank.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortTests::test_a_run_without_effort_reads_not_measured
  - **Verified:** yes (2026-11-15)
- **AC3:** Given reference-evidence-schema.md, when its report-of-record figure table is read, then it lists the new figure key with its section and meaning, and a run whose units carried two effort values reports each value with its unit count.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_effort.py::ReportEffortTests::test_the_annex_documents_the_figure_and_mixed_effort_is_counted
  - **Verified:** yes (2026-11-15)

## Notes

- Serves Abena Osei's End goal 3; delivers part of CR0699 (D0479).
- AC1 must fail on: the figure read from the config at report time rather than from the run record
- AC2 must fail on: an older run reported as inherit
- AC3 must fail on: a figure key the annex does not list, or a mixed run reported as one value
- Start from `_cost_roles_section` (sprint_report.py:4565-4601) and the NOT MEASURED convention (:2751). The annex's figure table is at reference-evidence-schema.md:200-230; the page is 746 lines, its ceiling 746 plus 5%, so a row or two fits.
- Shares sprint_report.py with CR0702-A and CR0702-B, which land in wave 1; this builds in wave 2.
- The new test carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
