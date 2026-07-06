# US0067: Triage noise controls: Medium-plus individual, Low consolidated, session cap

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0014
> **Persona:** Orchestrator / Operator
> **Source:** CR-0173 (workstream 3)

## User Story

**As an** operator drowning in agent-filed findings
**I want** built-in noise controls on artefact creation
**So that** the three findings that matter are not buried under a flood of Low-severity singletons

## Acceptance Criteria

### AC1: Severity-scaled filing

- **Given** a Low-severity single finding
- **When** it is filed
- **Then** it is redirected to a themed consolidation; Medium+ get individual artefacts
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py -k consolidate

### AC2: Session cap fails loud

- **Given** the configured per-session creation cap
- **When** the N+1th artefact is attempted
- **Then** creation is refused loudly
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py -k session_cap

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
