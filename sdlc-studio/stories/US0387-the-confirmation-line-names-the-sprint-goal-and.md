# US0387: the confirmation line names the Sprint Goal and the --goal rung distinctly, a test drives both cases

> **Status:** Draft
> **Delivers:** CR0387
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0143
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: The line that confirms a run opened distinguishes the Sprint Goal from the --goal ladder rung by

- **Given** {{context}}
- **When** {{action}}
- **Then** The line that confirms a run opened distinguishes the Sprint Goal from the --goal ladder rung by name, so neither can be read as the other
- **Verify:** {{executable check}}

### AC2: When a Sprint Goal was supplied it is shown as set, not reported as unset under a different field's

- **Given** {{context}}
- **When** {{action}}
- **Then** When a Sprint Goal was supplied it is shown as set, not reported as unset under a different field's name
- **Verify:** {{executable check}}

### AC3: When no Sprint Goal was supplied the line says so, since the workflow requires one and never

- **Given** {{context}}
- **When** {{action}}
- **Then** When no Sprint Goal was supplied the line says so, since the workflow requires one and never invents it
- **Verify:** {{executable check}}

### AC4: A test drives the plan both with and without --sprint-goal and asserts the confirmation text

- **Given** {{context}}
- **When** {{action}}
- **Then** A test drives the plan both with and without --sprint-goal and asserts the confirmation text differs, so the two cases cannot render identically
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
