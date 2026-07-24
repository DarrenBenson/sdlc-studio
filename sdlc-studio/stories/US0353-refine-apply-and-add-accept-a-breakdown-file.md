# US0353: refine apply and add accept a --breakdown file, validated whole before minting, equivalent to the --story form

> **Status:** Draft
> **Delivers:** CR0343
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0120
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: refine apply and refine add accept --breakdown <file> (JSON or YAML) describing the epic title (or

- **Given** {{context}}
- **When** {{action}}
- **Then** refine apply and refine add accept --breakdown <file> (JSON or YAML) describing the epic title (or --into target) and the stories (title, points, affects); it validates the whole file before minting anything (the existing fail-empty discipline) and is equivalent to the repeated --story form.
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
