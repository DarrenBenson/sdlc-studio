# US0588: A hand-rolled action carrying a filed gap id is reported and does not block; one without is outstanding

> **Status:** Draft
> **Delivers:** CR0515
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0196
> **Points:** 3

## User Story

**As a** agent facing a mechanical task with no tool
**I want** filing the gap to be the escape
**So that** the backlog improves instead of the rule eroding

## Acceptance Criteria

### AC1: a manual action citing a filed gap is reported and does not block

- **Given** a hand-rolled action recorded with the id of a CR filed for the missing tool
- **When** the checklist item resolves
- **Then** the action is reported with its gap id and the item is not outstanding, so the escape produces a backlog entry rather than a waiver
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ToolUseTests::test_a_cited_gap_does_not_block

### AC2: a manual action with no gap id is outstanding

- **Given** a hand-edited artefact with no gap recorded against it
- **When** the checklist item resolves
- **Then** it is OUTSTANDING and names the artefact, because hand-rolling around a tool that exists is the failure this item was built to surface
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ToolUseTests::test_an_uncited_manual_action_is_outstanding

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
