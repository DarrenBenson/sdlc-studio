# BG0865: The signed page names a known issue's retro ruling only when it is STOP-SHIP, and a finding the close files falls outside the run window

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issue_rulings.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG0865.md
> **Evidence:** BG0862 build (subagent a6f365ff), 2026-10-01; sprint_report._known_issues_section; _open_findings window
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T06:02:46Z

## Summary

Found building BG0862 (RUN-01M3T8N1, 2026-10-01): the goal 'Maya signs a report that names every operator ruling and carry' is false of the page. `sprint_report._known_issues_section` builds rows from close gaps (marked STOP-SHIP or 'close gap'), raw open-finding rows and carried units; a retro `## Known issues carried` ruling of not-stop-ship, accepted-risk or deferred never appears on the page - retro rulings reach only `sprint_report.py checklist`, which is not a page section. Separately the window is [start, end): the close files the graduation CR at the same instant it stamps `ended_at`, so the CR is outside the window and missing from the page's Known issues (seen at 01:56:30Z both).

## Steps to Reproduce

Build BG0862's end-to-end fixture (scratchpad `test_lean_signed_run_end_to_end.py)`: rule a carried bug not-stop-ship in the retro, close, sign, check - VALID, but the page has no 'not-stop-ship by Maya' and no graduation CR row.

## Proposed Fix

Give each Known issues row the ruling the retro recorded for it (ruling, ruled by), read from `retro.carried_issues` and fingerprinted with the page; replay a filed page's rows whole so pages filed before keep their fingerprint (RPT0011, RPT0012 stay VALID). Bound the window so a finding the close files is inside it (end inclusive, or the close's own filings counted).

## Acceptance Criteria

- [ ] **AC1** Given a run whose retro rules a carried bug not-stop-ship and an open finding accepted-risk, when the close files the report, then each of those Known issues rows names its ruling and who ruled it. Fails on: HEAD, whose rows carry no ruling unless STOP-SHIP
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issue_rulings.py::KnownIssueRulingTests::test_each_known_issue_names_its_retro_ruling
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given a close that files a graduation CR, then that CR is listed in the page's Known issues. Fails on: HEAD's [start, end) window, which excludes a finding filed at the close's own instant
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issue_rulings.py::KnownIssueRulingTests::test_a_finding_the_close_files_is_on_the_page
  - **Verified:** yes (2026-10-01)
- [ ] **AC3** Given this repository's signed RPT0011 and RPT0012, when `sprint_report.py check` runs after the change, then both print VALID. Fails on: a fix that re-derives old pages' rows with the new ruling column
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issue_rulings.py::KnownIssueRulingTests::test_signed_pages_stay_valid
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
