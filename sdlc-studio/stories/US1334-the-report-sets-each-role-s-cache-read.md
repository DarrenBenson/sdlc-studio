# US1334: The report sets each role's cache-read share against its mean over the last five signed runs

> **Status:** Done
> **Risk-class:** elevated
> **Delivers:** CR0753
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/scripts/tests/test_report_cache_read_trend.py, changelog.d/US1334.md, sdlc-studio/trd.md, sdlc-studio/prd.md
> **Epic:** EP0381
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who answers for what each team's delivery costs (Abena)
**I want** the run report to set each role's cache-read share against its mean over the last five signed runs
**So that** a role whose cache stopped working shows on the page of record against a baseline, not an impression

A new appendix section, `cache_read_trend`, after Cost by role, states per role this run's cache-read share (from the closing reading the Cost by role table states), the mean over the five most recent earlier signed pages that state a figure for that role, the change in points, and the pages it averaged. A page filed before the section renders as signed. One helper computes the baseline, so the close (US1335) reads the same mean the page states.

## Acceptance Criteria

### AC1: each role's share stands beside its five-run mean

- **Given** a fixture holding six signed pages whose Cost by role builder rows read 70.0% (signed first), then 63.2%, 64.9%, 67.1%, 62.6% and 62.9%, and a run whose closing reading gives the builder a 40.0% cache-read share
- **When** the report is built
- **Then** the `cache_read_trend` builder row states 40.0%, a mean of 64.1% over the five newest pages (the 70.0% page left out), a change of -24.1 points, and the five report ids. Fails on: HEAD, which builds no such section
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cache_read_trend.py::CacheReadTrendTests::test_each_role_share_stands_beside_its_five_run_mean
- **Verified:** yes (2026-11-26)
- **Caller:** `sprint close`, which files the page through `sprint_report.py`, and `sprint sign`, which re-derives it

### AC2: a role no earlier page measures reads not available, never 0

- **Given** the same pages with every reviewer row reading `not available`, and only two earlier pages carrying a repair row
- **When** the report is built
- **Then** the reviewer row's mean and change read not available with the reason that no earlier signed page states its share, and repair's mean is over the two pages it has and says two. Fails on: HEAD, which has no section, so an unmeasured role cannot be told from a measured 0
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cache_read_trend.py::CacheReadTrendTests::test_a_role_with_no_earlier_figure_reads_not_available
- **Verified:** yes (2026-11-26)
- **Caller:** `sprint close`, which files the page through `sprint_report.py`, and `sprint sign`, which re-derives it

### AC3: the section holds at sign, and an older page renders as signed

- **Given** a filed page carrying the section, after which the run's own page and one more page are signed; and a committed page filed before the section existed
- **When** the first page is re-derived at sign, and the older page is rendered to Markdown and HTML
- **Then** the section and the fingerprint are unchanged, because the run's own page and any page signed after this page was generated are never in its baseline, and the older page renders with no placeholder refused and no trend section. Fails on: HEAD, which has no section to hold
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cache_read_trend.py::CacheReadTrendTests::test_the_section_holds_at_sign_and_an_older_page_renders
- **Verified:** yes (2026-11-26)
- **Caller:** `sprint.py sign` (`cmd_sign`), which re-derives the filed page and refuses a changed one

### AC4: the evidence annex catalogues the section

- **Given** `reference-evidence-schema.md` and `sprint_report.EVIDENCE_SCHEMA_VERSION`
- **When** the annex's Report sections, figure keys and row keys tables are read
- **Then** `cache_read_trend` is listed as always, with a note under the table that a page filed before it carries none (as `cost_roles` has), each of its figure and row keys is catalogued, and the annex version and the constant both read 1.1. Fails on: HEAD, whose annex names no such section and where both read 1.0
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cache_read_trend.py::CacheReadTrendTests::test_the_annex_catalogues_the_section_at_version_1_1
- **Verified:** yes (2026-11-26)
- **Caller:** `tests/test_evidence_annex_report.py`, which holds the annex to every section a filed page carries

## Notes

- No code dependency on BG1764. Every signed page from RPT0026 to RPT0045 reads `not available` for the reviewer's cache-read share, so the reviewer has no baseline until signed runs after BG1764 carry one; AC2 states that as not available.
- Real baseline today (RPT0041 to RPT0045): orchestrator 81.8%, builder 64.1%, repair 61.2%, other 48.9%, reviewer not available.
- Read earlier pages with `_signed_reports` and `_section_of`; parse the `role_cache_read` cell (`"62.9%"`), skipping `not available` and NOT MEASURED cells. The run's own share comes from the same reading `_cost_roles_section` states; when that section is NOT MEASURED, so is the trend, with its reason.
- Add a new section rather than columns on `cost_roles`: `_render` refuses any placeholder a page has no figure for, so a trend placeholder on the Cost by role row would make every page filed before it unrenderable.
- Either replay the section from the page at re-derivation, as `_page_readings` replays the role table, or take only pages signed before the page's `generated_at`; AC3 holds either way.
- Expose the baseline as one function (for example `cache_read_baseline(root, run_id, before)`) for US1335 to call.
- Versioning: one minor bump for the release. US1338 adds its section under 1.1 and does not bump again. `test_evidence_schema_stamp.py` checks the constant against the masthead.
- Grounded at HEAD db54c42bb on 2026-11-26:
  - AC1 to AC3: `test_sprint_report.fixture_run(root)` then `sprint_report.build_report(root, FIX_RETRO)` gave the sections goal, estimates, delivered, known_issues, signoff, cost, cost_prices, cost_roles, dora, calibration, rulings, waivers and lessons, with no trend section.
  - AC2: a scan of `sdlc-studio/reports/RPT*.json` found 20 signed pages carrying `cost_roles`, with every reviewer `role_cache_read` reading `not available`.
  - AC3: `sprint_report._render` raises `ReportError` naming each placeholder no figure answers, and `render_context` sets `<section>_present` only for sections the page carries.
  - AC4: `grep -c cache_read_trend` on `reference-evidence-schema.md` and `sprint_report.py` printed 0 and 0; `EVIDENCE_SCHEMA_VERSION = "1.0"` and the annex masthead reads 1.0; `test_evidence_annex_report.py` passed its 3 tests in 4.60 s.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Groomed for run twenty-eight from the D0635 breakdown |
| 2026-11-26 | orchestrator | Affects names sdlc-studio/trd.md and sdlc-studio/prd.md: AC4's annex bump to 1.1 makes both pages' 'annex version 1.0' untrue, and `test_lean_specs_v64` reads the TRD's |
| 2026-11-26 | orchestrator | AC4 re-ruled (D0644): `cache_read_trend` is catalogued as always with a filed-before note, as `cost_roles` is; the conditional form could not hold beside the annex catalogue test |
