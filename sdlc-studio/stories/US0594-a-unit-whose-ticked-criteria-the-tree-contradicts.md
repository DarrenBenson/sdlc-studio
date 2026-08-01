# US0594: A unit whose ticked criteria the tree contradicts is reported outstanding at the close

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0197
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a tick the tree contradicts is outstanding at the close

- **Given** a unit whose criteria are ticked while the surfaces they name are unchanged since the run's base ref
- **When** the checklist resolves
- **Then** the item is OUTSTANDING and names the unit and the criterion, because two units of one run were closed on exactly this and the checklist passed them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationTests::test_a_tick_the_tree_contradicts_is_outstanding

### AC2: a tick the tree supports passes

- **Given** a unit whose ticked criteria name surfaces the run did change
- **When** the checklist resolves
- **Then** the item passes - the control against an item that flags every ticked criterion
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationTests::test_a_supported_tick_passes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
