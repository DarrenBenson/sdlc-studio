# US0146: Record the consult on the artefact: which seats were consulted and the questions

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Epic:** EP0040
> **Points:** 3

## User Story

**As a** reviewer or auditor
**I want** the consulted seats and questions recorded on the request/Issue
**So that** the audit trail shows who was asked and what, not just a line in stdout.

## Acceptance Criteria

### AC1: refine/triage record the consult (line + section + questions), idempotently, only when there are questions

- **Given** a refine/triage with `--question`
- **When** the ceremony runs (and a re-run)
- **Then** the request/Issue carries a `> **Consulted:**` line and an `## Amigo Consult` section listing the questions, written once (no duplication on re-run); a run with no questions records nothing; the recorded artefact still validates and reconciles clean
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_amigo_consult.ConsultRecordTests
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
