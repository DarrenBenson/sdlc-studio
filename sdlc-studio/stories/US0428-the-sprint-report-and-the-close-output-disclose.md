# US0428: the sprint report and the close output DISCLOSE every delegated sign-off, naming the delegate

> **Status:** Done
> **Delivers:** RFC0051
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0159
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the sprint report discloses every delegated sign-off

- **Given** a run containing both delegated and human sign-offs
- **When** the sprint report is composed
- **Then** each delegated one is named with its delegate, and the count is stated - a reader must be able to see how much of a sprint was signed by agents without reading every row
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DisclosureTests::test_every_delegated_signoff_is_named_with_its_delegate
- **Verified:** yes (2026-07-24)

### AC2: the close output discloses it too

- **Given** the same run
- **When** `sprint close` runs
- **Then** the disclosure appears in the close output, not only in the report - the close is what the operator reads at the moment of the decision
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DisclosureTests::test_the_close_output_discloses_delegated_signoffs
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
