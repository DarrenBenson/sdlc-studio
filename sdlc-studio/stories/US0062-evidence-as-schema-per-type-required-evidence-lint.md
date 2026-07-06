# US0062: Evidence-as-schema: per-type required evidence, lint-enforced

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0013
> **Persona:** Skill Maintainer
> **Source:** CR-0171
> **Depends on:** US0060

## User Story

**As a** sampling human auditor
**I want** the evidence-or-it-did-not-happen rule promoted to lint-enforced structure per type
**So that** every finding carries machine-checkable evidence before its quality is even assessed

## Acceptance Criteria

### AC1: Per-type evidence required

- **Given** a bug with no file:line, command output, or reproduction; or a CR with no impact
  or effort estimate
- **When** the lint runs
- **Then** it fails, naming the accepted evidence forms; placeholders count as absent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k evidence_schema

### AC2: Legacy artefacts exempt (era-gated)

- **Given** an artefact predating schema v3
- **When** the lint runs
- **Then** it passes untouched
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py -k evidence_era_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
