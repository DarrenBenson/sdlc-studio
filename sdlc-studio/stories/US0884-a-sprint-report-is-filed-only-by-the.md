# US0884: A sprint report is filed only by the close

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py
> **Epic:** EP0261
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator signing a report
**I want** a report filed only through the close
**So that** no page reaches me without the close's token stamp and checks (BG0744)

## Acceptance Criteria

- **AC1:** Given an open run, when `sprint_report.py` build --write runs, then it refuses and names sprint close, writing no report; without --write it previews to stdout
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::FiledByCloseTests::test_build_write_refuses_while_the_run_is_open
  - **Verified:** yes (2026-09-24)
- **AC2:** Given the same run, when sprint close runs, then the report is filed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::FiledByCloseTests::test_the_close_still_files_the_report
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
