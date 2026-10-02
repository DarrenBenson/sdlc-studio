# BG0912: The close files a report for sign-off without putting the readable page in front of the operator

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_shows_the_page.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M3Y7DP close, operator: 'Where's the report, you must make it available before I can sign'
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T16:45:29Z

## Summary

sprint close ends with 'sign it with: sprint.py sign --report RPTxxxx', but prints neither the page's path nor its rendered HTML, so the operator is asked to sign a report they have not been shown; the HTML rendering exists (`sprint_report.py` render --to html) but nothing produces it at the close.

## Steps to Reproduce

1. sprint close a run. 2. Read the last lines -> a sign command and a fingerprint, no path to the page and no rendered HTML.

## Proposed Fix

At the close, write the HTML twin beside the report (reports/RPTxxxx.html) and print the paths of the markdown page and the HTML twin above the sign command.

## Acceptance Criteria

- [ ] **AC1** Given a run that closes and files RPT0001, when sprint close finishes, then reports/RPT0001.html exists and the output names the markdown page's path and the HTML twin's path before the sign command. Fails on: the current close prints only the sign command
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_shows_the_page.py::CloseShowsThePageTests::test_the_close_names_the_page_and_its_html_twin

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
