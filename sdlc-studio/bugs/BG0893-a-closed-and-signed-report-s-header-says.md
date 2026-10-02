# BG0893: A closed and signed report's header says the run window ends 'to open'

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_window_header.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RPT0014 header
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:54Z

## Summary

RPT0014 reads 'Run: 2026-10-01T10:19:17Z to open (9.6h)' though the page records `window_end` 2026-10-01T19:54:55Z and the run is sealed; the header is rendered while the run is still open at the close and never names the end it measured to.

## Steps to Reproduce

1. sprint close a run. 2. Read the page header -> 'to open'.

## Proposed Fix

Render the window end the page derived to (`window_end)`, not the run's open state.

## Acceptance Criteria

- [ ] **AC1** Given a page derived at the close with `window_end` 2026-10-01T19:54:55Z, when it renders, then the header names that end and never 'to open'. Fails on: the current code prints 'to open'
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_window_header.py::ReportWindowHeaderTests::test_the_header_names_the_window_end

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
