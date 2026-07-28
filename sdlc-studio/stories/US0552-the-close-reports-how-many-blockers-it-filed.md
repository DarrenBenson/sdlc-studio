# US0552: The close reports how many blockers it filed and how many distinct causes they represent, so a fan-out is visible when it happens

> **Status:** Review
> **Delivers:** CR0495
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0188
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** an operator watching a close file its outstanding work
**I want** the close to report how many artefacts it filed and how many distinct causes they represent
**So that** a fan-out is visible at the moment it happens rather than discovered in the backlog later

## Acceptance Criteria

### AC1: the close reports filings and distinct causes

- **Given** a bounded exit that filed blockers
- **When** the close reports
- **Then** it states how many artefacts were filed and how many distinct causes they represent, so a fan-out is visible when it happens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseGroupingTests::test_the_close_reports_filings_and_cause_count
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
