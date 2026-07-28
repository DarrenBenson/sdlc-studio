# US0540: The close reports seam coverage beside the points, and a batch that shipped with unowned seams says so

> **Status:** Draft
> **Delivers:** CR0468
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0184
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the close reports seam coverage, including what was left unowned

- **Given** a batch that shipped with one or more seams nobody owned
- **When** the close reports
- **Then** seam coverage appears beside the points and the unowned seams are named rather than omitted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SeamCoverageTests::test_unowned_seams_are_named_at_close

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
