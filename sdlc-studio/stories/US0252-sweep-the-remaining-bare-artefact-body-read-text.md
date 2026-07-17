# US0252: sweep the remaining bare artefact-body read_text calls through read_text_safe, with a regression test

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0082
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: route each artefact-body `read_text(encoding`=utf-8) through `read_text_safe` (index-file reads

- **Given** {{context}}
- **When** {{action}}
- **Then** route each artefact-body `read_text(encoding`=utf-8) through `read_text_safe` (index-file reads stay loud)
- **Verify:** {{executable check}}

### AC2: a regression test drives a representative scanner with a non-UTF-8 artefact and asserts no crash

- **Given** {{context}}
- **When** {{action}}
- **Then** a regression test drives a representative scanner with a non-UTF-8 artefact and asserts no crash
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
