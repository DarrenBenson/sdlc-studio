# US0254: gate --release runs check_versions --strict under one exit code; a CHANGELOG mismatch fails

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, sdlc-studio/tsd.md
> **Epic:** EP0082
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: gate.py --release runs `check_versions` --strict (or an equivalent mechanical release step does)

- **Given** {{context}}
- **When** {{action}}
- **Then** gate.py --release runs `check_versions` --strict (or an equivalent mechanical release step does), so a CHANGELOG version mismatch fails the release gate with one exit code
- **Verify:** {{executable check}}

### AC2: A test asserts gate --release fails on a CHANGELOG/version-home disagreement

- **Given** {{context}}
- **When** {{action}}
- **Then** A test asserts gate --release fails on a CHANGELOG/version-home disagreement
- **Verify:** {{executable check}}

### AC3: tsd.md stage-4 and gate-table wording match the mechanical reality; the release-gate.md checklist

- **Given** {{context}}
- **When** {{action}}
- **Then** tsd.md stage-4 and gate-table wording match the mechanical reality; the release-gate.md checklist bullet becomes redundant confirmation rather than the only enforcement
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
