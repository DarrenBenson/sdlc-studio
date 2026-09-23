# US0883: A signed report cannot be edited unnoticed

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py
> **Epic:** EP0261
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator auditing a signed report
**I want** check to notice any edit to a filed page's own figures
**So that** a page I signed cannot be changed afterwards without check saying so (BG0745)

## Acceptance Criteria

- **AC1:** Given a filed report, when a figure in its JSON is edited, then `sprint_report.py` check reads INVALID and names the edited figure, although the tree still re-derives the original
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::PageIntegrityTests::test_an_edited_json_figure_is_invalid
- **AC2:** Given a filed report, when a figure in its markdown page is edited, then check reads INVALID and names it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::PageIntegrityTests::test_an_edited_markdown_figure_is_invalid
- **AC3:** Given a report signed with sprint sign, then the signature row it writes does not trip the check, which stays VALID
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_integrity.py::PageIntegrityTests::test_the_signature_does_not_invalidate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
