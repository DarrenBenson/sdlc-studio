# US0076: Harmonise the config failure regimes with a warn on unhonoured override

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0018
> **Persona:** Skill Maintainer
> **Source:** CR-0180

## User Story

**As a** consuming-project operator
**I want** the three config failure regimes harmonised so an unhonoured override is never silent
**So that** my declared conventions are not quietly ignored, and the README dependency claim is honest

## Acceptance Criteria

### AC1: Visible diagnostic on an unhonoured override

- **Given** a `.config.yaml` present but unreadable (no PyYAML or malformed)
- **When** project_override reads it
- **Then** it emits a one-line stderr diagnostic instead of silently reverting to defaults
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py -k override_warn

### AC2: Docs match reality

- **Given** the config/gate paths
- **When** the README/AGENTS dependency claim is checked
- **Then** it matches (config either works stdlib-only or states PyYAML is needed)
- **Verify:** manual review of the dependency statement

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
