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
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/schema_check.py check --root .
- **Verified:** yes (2026-09-26)

### AC2: Each rule is a tested worked example

- **Given** each rule
- **When** its fixture runs
- **Then** the failure message names the rule and the fix (a reference implementation for the crew linter)
- **Verify:** manual - retired by US0944: no live test proves it. `test_audit_check.py` went with the US0345-US0346 rename, and its successor `test_schema_check.py` exercises two of the seven rules and asserts rule-id membership only, never the message or a fix hint
- **Verified:** manual (2026-09-25) - retired, superseded by US0944

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-09-25 | US0944 | AC2 retired in the D0259 pattern: its stamp named `test_audit_check.py`, gone since the US0345-US0346 rename, and `test_schema_check.py` does not prove each rule's message names the rule and the fix |
| 2026-09-26 | US0940 | AC1 re-pointed: US0345-US0346 (0288bd76) renamed `audit_check.py` to `schema_check.py`; the same command over this repository |
