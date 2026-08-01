# US0602: A panel-signed unit is distinguishable from an operator-signed one forever, in the signoff record and in the sprint report

> **Status:** Ready
> **Delivers:** CR0514
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0198
> **Points:** 3

## User Story

**As a** auditor reading the record months later
**I want** a panel-signed unit distinguishable from an operator-signed one
**So that** who accepted this never becomes ambiguous

## Acceptance Criteria

### AC1: the record says which signed it

- **Given** one unit signed by a panel and one by the operator
- **When** the signoff record is read back
- **Then** each row states which, so the two are distinguishable without inference
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffProvenanceTests::test_panel_and_operator_rows_are_distinguishable

### AC2: the sprint report carries the distinction too

- **Given** a closed run mixing both
- **When** the sprint report renders
- **Then** it reports the split rather than a single sign-off count, because a total hides exactly the fact an auditor came for
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SignoffProvenanceTests::test_the_report_splits_panel_from_operator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
