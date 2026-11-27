# US1348: The sprint report shows first-round approval and rounds per unit for units that took the solution review and units that did not

> **Status:** Done
> **Risk-class:** elevated
> **Delivers:** CR0756
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_report.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py, changelog.d/US1348.md
> **Epic:** EP0385
> **Points:** 3
> **Depends on:** US1344
> **Persona:** Abena Osei

## User Story

**As** the person paying for the runs, **I want** the run report to set first-round approval and
rounds per unit for units that took the solution review beside those that did not, **so that**
whether the step saves money is a figure on the page of record.

## Acceptance Criteria

### AC1: the two groups stand side by side

- **Given** a run of three units: one with CHANGES then GO and a round-one APPROVE, one with GO
  and a REJECT then APPROVE, and one with no solution review and a REJECT then APPROVE
- **When** the report is built
- **Then** the `solution_review` section's took row reads 2 units, 1 first-round approval, 50%,
  1.5 delivery rounds per unit and 1.5 solution review rounds per unit, and its did-not row reads
  1 unit, 0, 0% and 2.0. Fails on: HEAD, whose fixture report builds no such section.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_report.py::SolutionReviewReportTests::test_the_two_groups_stand_side_by_side
- **Verified:** yes (2026-11-27)

### AC2: a run where no unit took the step reads not measured

- **Given** a run whose units have delivery verdicts and no solution review rows
- **When** the report is built
- **Then** the section reads NOT MEASURED with the reason that no unit in the run took a
  solution review, and never 0%. Fails on: HEAD, which has no such section.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_report.py::SolutionReviewReportTests::test_a_run_where_no_unit_took_the_step_reads_not_measured
- **Verified:** yes (2026-11-27)

### AC3: the section holds at sign, and an older page renders as signed

- **Given** a filed page carrying the section, after which one more solution review row is
  recorded for one of its units; and a committed page filed before the section existed
- **When** the first page is re-derived at sign, and the older page is rendered to Markdown and
  HTML
- **Then** the section and the fingerprint are unchanged because the rows were frozen at close,
  and the older page renders with no placeholder refused and no solution review section. Fails
  on: HEAD, which has no section to hold.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_report.py::SolutionReviewReportTests::test_the_section_holds_at_sign_and_an_older_page_renders
- **Verified:** yes (2026-11-27)

### AC4: the evidence annex catalogues the section

- **Given** reference-evidence-schema.md and `sprint_report.EVIDENCE_SCHEMA_VERSION`
- **When** the annex's Report sections, figure keys and row keys tables are read
- **Then** `solution_review` is listed as always, with a note that a page filed before it
  carries none, each of its figure and row keys is catalogued, both the annex and the constant
  still read 1.1, and the annex is within its line ceiling. Fails on: HEAD, where the annex has 0
  mentions of `solution_review`.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_solution_review_report.py::SolutionReviewReportTests::test_the_annex_catalogues_the_section
- **Verified:** yes (2026-11-27)

## Notes

- Ran: `test_sprint_report.fixture_run` then `sprint_report.build_report`: 14 sections, no
  `solution_review`; the constant reads 1.1 (Evidence S5).
- A new section rather than columns on the Delivered table: `_render` refuses any placeholder a
  page has no figure for, so a new placeholder on an existing row would make every earlier page
  unrenderable. Gate the template block on `solution_review_present`, which `render_context`
  sets only for sections a page carries.
- Version: the release's minor bump to 1.1 has landed (US1334, 2ec5c5cd4); add under 1.1, as
  US1338 does; `test_evidence_schema_stamp` checks the constant against the masthead.
- "Delivery rounds per unit" counts as the Delivered table's `unit_rounds` does, so the two
  figures agree on one page.
- Beside the existing tests: templates are read by test_sprint_report (whose template prose
  check refuses numerals: keep the block's prose free of digits), test_lean_lessons and
  test_lean_report_integrity; the annex by 7 modules, among them test_evidence_annex_report
  (every section a filed page carries must be catalogued, which AC4 meets),
  test_evidence_annex_ledgers (four named ledgers; the new ledger need not join it) and
  test_evidence_annex_run_record (S5 adds no run-record key: it reads the committed ledger).
- Budget: reference-evidence-schema.md is 763 lines against a ceiling of 783 (746 base). Keep
  S5's additions to 8 lines; US1338 and US1235 also add to it.
- D0647 (product seat): add a tokens-per-unit column to both rows if the run's actuals already carry tokens per unit; if they do not, say so in the section and leave the bar judged on first-round approval and rounds.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | orchestrator (D0545) | Groomed: criteria with Fails on run at HEAD and Verify nodes, from the engineering seat's draft; default and this repository's setting per D0647 (product seat). |
| 2026-11-26 | orchestrator (D0545) | Affects gains `scripts/tests/test_evidence_annex_report.py`: the annex fixture's full run has no solution-review row and must carry one to show the section (approach review item 3, D0646 pilot). |
