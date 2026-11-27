# US1235: The sprint report and the seat scorecard show the release change failure rate, naming its source records

> **Status:** Done
> **Depends on:** US1234, US1335
> **Risk-class:** elevated
> **Delivers:** CR0695
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/help/retro.md, .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py, changelog.d/US1235.md, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py
> **Epic:** EP0339
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who takes each release to the change board (Abena)
**I want** the run report and the seat scorecard to show the release change failure rate, with
the release records and incident issues it was read from
**So that** the page of record carries the figure the board asks for, from the same calculation
the command prints, and says not measured where nothing was recorded

## Context

### Background

US1234 derives the rate. This story puts it on the report, in a new appendix section
`release_cfr` after the DORA table, and on `retro.py seats`, both through US1234's one function.
The DORA table's own "Change failure rate" row counts CI push runs and stays as it is. A page
filed before the section renders as signed, and a signed page stays VALID when an incident is
linked to one of its releases later, because the release records and incident issues move after
the run as the lesson store does.

---

## Acceptance Criteria

### AC1: the report states the release rate with its source records, beside an unchanged DORA table

- **Given** a closed fixture run (`test_sprint_report.fixture_run`) in a project whose release record file holds four settled releases and an incident issue linked to one of them
- **When** the report is built through `sprint_report.build_report` and rendered to Markdown and HTML
- **Then** a `release_cfr` section after the DORA table states 25% (1 of 4) with its window and settling period, a row per release counted citing the release record file, and the failed release's row naming its incident issue and escaped bug; and the DORA table's "Change failure rate" row is present and unchanged. Fails on: HEAD, whose fixture report builds the sections goal, estimates, delivered, known_issues, signoff, cost, cost_prices, cost_roles, dora, calibration, rulings, waivers and lessons and no release rate (built 2026-11-26); or the release figure merged into the CI-run row
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py::ReportChangeFailureRateTests::test_the_report_shows_the_release_rate_with_its_source_records
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint close`, which files the page through `sprint_report.py`, and `sprint sign`, which re-derives it

### AC2: the seat scorecard shows the figure the command derives

- **Given** the same project and a retro naming the run's batch
- **When** `retro.py seats --id RETROxxxx` runs, as text and with `--format json`
- **Then** the scorecard states the release change failure rate with the release records and incident issues it read, and its rate and its counted, failed and pending releases equal what `escape.py failure-rate` prints for the same window. Fails on: HEAD, whose scorecard names no failure rate (on RETRO0159 its JSON keys are id, recorded_in_error_unattributed, rows, seats, unattributed, unattributed_authors, uncharged, units and window); or a second calculation that can disagree with the command
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py::ReportChangeFailureRateTests::test_the_seat_scorecard_shows_the_figure_the_command_derives
- **Verified:** yes (2026-11-27)
- **Caller:** `retro.py seats`, run at the retro and read by the persona learn-brief (`persona_memory.py learn-brief`)

### AC3: not measured and pending reach the page

- **Given** a project with no release record, and one whose only release is inside the settling period
- **When** the report is built and rendered to Markdown and HTML in each
- **Then** the section reads NOT MEASURED with the command's reason in the first, and NOT MEASURED naming the release as pending in the second, never 0% and never an empty cell, and both templates carry the section. Fails on: HEAD, which has no section; or 0% or a blank where nothing was measured
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py::ReportChangeFailureRateTests::test_not_measured_and_pending_reach_the_report
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint_report.py render`, which renders a filed page to Markdown and HTML

### AC4: a signed page holds when an incident is linked later, and an older page renders

- **Given** a page filed with the section and signed, after which an incident issue is triaged into an escaped bug of a release the page counted; and a committed page filed before the section existed
- **When** `sprint_report.py check` runs on the first, and the second is rendered to Markdown and HTML
- **Then** the first reads VALID and still shows the rate it was signed with, and the second renders with no placeholder refused and no release-rate section. Fails on: HEAD, which has no section; or a section inside the fingerprint and re-derived from the moved records, which reads INVALIDATED on the next incident, the failure RPT0006 to RPT0008 showed for the lesson store
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py::ReportChangeFailureRateTests::test_a_signed_page_holds_and_an_older_page_renders
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint.py sign` (`cmd_sign`), which re-derives the filed page and refuses a changed one

### AC5: the evidence annex catalogues the section

- **Given** `reference-evidence-schema.md` and `sprint_report.EVIDENCE_SCHEMA_VERSION`
- **When** the annex's Report sections, figure keys and row keys tables are read
- **Then** `release_cfr` is listed as an always section, with a note under the table that a page filed before it carries none and how a signed page keeps it (D0651, as D0644 ruled for cache_read_trend), and each of its figure and row keys is catalogued, under the annex version US1334 sets for the release, with no second bump. Fails on: HEAD, where `grep -c release_cfr` prints 0 for the annex and for `sprint_report.py`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_change_failure_rate.py::ReportChangeFailureRateTests::test_the_annex_catalogues_the_section
- **Verified:** yes (2026-11-27)
- **Caller:** `tests/test_evidence_annex_report.py`, which holds the annex to every section a filed page carries

---

## Scope

### In Scope

- The `release_cfr` report section, its Markdown and HTML blocks and its annex entries
- One line (and one JSON key) on `retro.py seats`, documented in `help/retro.md`
- Keeping the section out of what a later incident can invalidate

### Out of Scope

- The calculation itself (US1234)
- Escapes per 100 points, which CR0695 places beside the rate: no report or scorecard carries it, and its story (US1254, EP0346) is Draft and not in v6.5.0
- Any change to the DORA table

---

## Technical Notes

- Grounded at HEAD af477fc6d on 2026-11-26: `grep -c "release_cfr\|failure_rate"` prints 0 for `sprint_report.py`, `retro.py`, the Markdown template and the annex; `SECTIONS_OUTSIDE_THE_DIGEST` is `("lessons", "lane_yield")`; `EVIDENCE_SCHEMA_VERSION` is `1.0`.
- Read the figure through US1234's function only. The window is the command's default, the 90 days ending at the page's window end, and the settling period its default.
- A new section, not new columns: `_render` refuses any placeholder a page has no figure for, and `render_context` sets `<key>_present` only for the sections a page carries, so a page filed before renders as signed.
- Stability: put `release_cfr` in `SECTIONS_OUTSIDE_THE_DIGEST`, as `lessons` is, or replay it from the filed page as `_page_readings` does; AC4 holds either way. The annex says which.
- Versioning: US1334 bumps the annex and the constant to 1.1 for the release; US1338 and this story add under 1.1 (`test_evidence_schema_stamp.py` checks the constant against the masthead).
- Budget: `reference-evidence-schema.md` is 754 lines against a hard limit of 783 (746 x 1.05 in `tools/check_budgets.py`), and US1334 and US1338 add to it first. If the budgets lane refuses, tighten the new prose; raising the ceiling is outside this unit's Affects and needs a logged decision.
- The scorecard: `retro.seat_record` and `render_seat_evidence`; `help/retro.md` documents `retro.py seats` at line 57.
- Run twenty-eight: `sprint_report.py` is edited in turn by US1334, US1338, US1294, US1234 and this story, which is last; the two templates and the annex by US1334, US1338 and this story; `retro.py` by US1335 and this story.
- New test module carries `# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py`.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| The release record file has an unparsable line | The section is NOT MEASURED naming the line; the page is still filed |
| Every release in the window is pending | NOT MEASURED, naming the pending releases |
| An incident is linked after the page is signed | The signed page keeps its figure and checks VALID (AC4) |
| A page filed before the section | Renders with no section and no refused placeholder (AC4) |
| The retro carries no Date | The scorecard reads the command's default window and says so |

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| US1234 | Blocking | The one function the section and the scorecard read; last before this story on `sprint_report.py` | Draft |
| US1335 | Sequencing | Edits `retro.py` first | Ready |
| US1334, US1338 | Sequencing | Edit the templates, the annex and `sprint_report.py` first; reached through US1234 and US1294 | Ready |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Re-grounded against HEAD for run twenty-eight (D0638) |
| 2026-11-27 | orchestrator (D0545) | AC5 re-ruled under D0651 (always section plus a note, as D0644), and Affects gains `tests/test_evidence_annex_report.py`, whose full fixture the section needs: both raised by the approach panel before coding |
