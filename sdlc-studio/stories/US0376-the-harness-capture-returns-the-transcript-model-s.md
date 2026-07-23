# US0376: the harness capture returns the transcript model(s), mixed as mixed, and the close writes it to the Model cell

> **Status:** Draft
> **Delivers:** CR0373
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0134
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: `harness_tokens` also returns the model(s) seen in the session transcript, mixed reported as mixed

- **Given** {{context}}
- **When** {{action}}
- **Then** `harness_tokens` also returns the model(s) seen in the session transcript, mixed reported as mixed
- **Verify:** {{executable check}}

### AC2: the velocity row written by an interactive close carries that model in its Model cell, so

- **Given** {{context}}
- **When** {{action}}
- **Then** the velocity row written by an interactive close carries that model in its Model cell, so `measured_rate` books it in the right (project, model) cell
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
