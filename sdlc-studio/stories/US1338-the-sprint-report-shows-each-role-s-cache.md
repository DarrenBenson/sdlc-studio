# US1338: The sprint report shows each role's cache-write growth and re-writes after expiry

> **Status:** Done
> **Depends on:** US1333, US1334, US1337
> **Risk-class:** elevated
> **Delivers:** RFC0069
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/reference-evidence-schema.md, .claude/skills/sdlc-studio/scripts/tests/test_report_cache_writes.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_annex_report.py, changelog.d/US1338.md
> **Epic:** EP0383
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who answers for what each team's delivery costs (Abena)
**I want** the run report to show each role's cache-write growth and re-writes after expiry
**So that** the change board reads on the page of record how much cache spend each role lost to waiting

The closing reading keeps each role's split from the anatomy, and a new appendix section, `cost_cache_writes`, states per role the growth, the re-writes after 5-minute and after 1-hour expiry, and the re-write share of the role's cache writes. A page filed before the section renders as signed, and the section is replayed at sign.

## Acceptance Criteria

### AC1: the page states each role's split from the closing reading

- **Given** a fixture run whose closing reading recorded the anatomy of US1337's fixture
- **When** the report is built
- **Then** the `cost_cache_writes` section states the orchestrator's 2,500 growth and 9,000 re-written after 1-hour expiry, the subagent role's 3,800 growth and 4,000 re-written after 5-minute expiry, and each role's re-write share. Fails on: HEAD, whose closing stamp keeps only `run_state._ROLE_KEYS`, so any key the anatomy adds is dropped before the page can read it, and whose page has no such section
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cache_writes.py::CacheWritesReportTests::test_the_page_states_each_roles_split_from_the_closing_reading
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint close`, whose `_file_the_report` calls `run_state.stamp_cost_roles` and files the page

### AC2: a reading with no split reads NOT MEASURED, and an older page renders as signed

- **Given** a run whose closing reading was stamped before the split existed, and a committed page filed before the section
- **When** the first is reported and the second rendered to Markdown and HTML
- **Then** the first page's section reads NOT MEASURED with the reason that its reading recorded no split, and the older page renders with no placeholder refused and no such section. Fails on: HEAD, which has no section to say NOT MEASURED in
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cache_writes.py::CacheWritesReportTests::test_no_split_reads_not_measured_and_an_older_page_renders
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint close`, which files the page through `sprint_report.py`

### AC3: the section is replayed at sign and catalogued in the annex

- **Given** a filed page carrying the section, after which the session's transcript grows
- **When** the page is re-derived at sign
- **Then** the section and the fingerprint are unchanged (replayed from the page as `_page_readings` replays the Cost by role table), and the annex lists `cost_cache_writes` with its figure and row keys under version 1.1. Fails on: HEAD, whose annex names no such section
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cache_writes.py::CacheWritesReportTests::test_the_section_is_replayed_at_sign_and_catalogued
- **Verified:** yes (2026-11-27)
- **Caller:** `sprint.py sign` (`cmd_sign`), which re-derives the filed page and refuses a changed one

## Notes

- Depends on US1337 (the split), US1334 (the same report files, and the annex already at 1.1) and US1333 (both edit `lib/run_state.py`).
- No version bump: US1334 moves the annex to 1.1 for the release, and this section is catalogued under it.
- Add the split's key to `run_state._ROLE_KEYS` so the closing stamp keeps it.
- Grounded at HEAD db54c42bb on 2026-11-26:
  - AC1: with `cost_anatomy.anatomy` wrapped to add a `cache_writes` key to every role, `run_state._cost_roles(<fx>, ...)` returned role keys agents, avg_context, calls, first_context, priced, role, share and split: the added key was dropped.
  - AC1, AC2: `build_report` on `test_sprint_report.fixture_run` gave no cache-writes section (goal through lessons, as US1334 lists).
  - AC3: `grep -c cost_cache_writes` on `reference-evidence-schema.md` and `sprint_report.py` printed 0 and 0.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Groomed for run twenty-eight from the D0635 breakdown |
| 2026-11-26 | orchestrator (D0545) | Affects gains `scripts/tests/test_evidence_annex_report.py`: the annex fixture asserts the section order the new cache-writes section joins (approach review, D0646 pilot). |
