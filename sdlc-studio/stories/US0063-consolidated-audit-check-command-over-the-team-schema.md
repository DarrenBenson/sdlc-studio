# US0063: Consolidated audit-check command over the team-schema rules

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0013
> **Persona:** Skill Maintainer
> **Source:** CR-0174
> **Depends on:** US0060, US0061, US0062

## User Story

**As a** CI and pre-commit gate
**I want** one command that runs all the schema-v3 team rules with one exit code
**So that** the rules are enforced together, not skipped individually, and feed the crew audit linter

## Acceptance Criteria

### AC1: One command, six rules, non-zero on any violation

- **Given** the rule set (authorship, evidence, duties, index-derived, id-format, tranche-shape)
- **When** the command runs
- **Then** it exits non-zero on any violation with a stable rule id and fix hint, zero on a clean repo
- **Verify:** python3 .claude/skills/sdlc-studio/scripts/gate.py --only audit-check

### AC2: Each rule is a tested worked example

- **Given** each rule
- **When** its fixture runs
- **Then** the failure message names the rule and the fix (a reference implementation for the crew linter)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_check.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
