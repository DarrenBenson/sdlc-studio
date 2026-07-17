# US0225: resolve/document the report.enabled json exemption and test the json path

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-scripts-domain.md
> **Epic:** EP0074
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: The json exemption is either removed (gate covers both formats) or documented as page-vs-data in

- **Given** {{context}}
- **When** {{action}}
- **Then** The json exemption is either removed (gate covers both formats) or documented as page-vs-data in the code comment, `rendering_enabled` docstring, the disabled notice text, and reference-scripts-domain.md
- **Verify:** {{executable check}}

### AC2: A ConfigGateTest covers the json path against a disabled config, asserting whichever behaviour was

- **Given** {{context}}
- **When** {{action}}
- **Then** A ConfigGateTest covers the json path against a disabled config, asserting whichever behaviour was chosen
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
