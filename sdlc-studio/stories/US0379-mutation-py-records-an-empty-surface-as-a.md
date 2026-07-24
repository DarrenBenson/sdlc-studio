# US0379: mutation.py records an empty surface as a first-class outcome and the gate lane reads it distinct from not-run and PASSes

> **Status:** Draft
> **Delivers:** CR0376
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0137
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: mutation.py run over a surface with no mutatable files can emit a report recording the empty

- **Given** {{context}}
- **When** {{action}}
- **Then** mutation.py run over a surface with no mutatable files can emit a report recording the empty surface as the honest outcome (exit 0 under an explicit flag or a distinct recorded status), never a silent pass
- **Verify:** {{executable check}}

### AC2: the gate's mutation lane reads that report as 'nothing to mutate' - distinct from not-run and from

- **Given** {{context}}
- **When** {{action}}
- **Then** the gate's mutation lane reads that report as 'nothing to mutate' - distinct from not-run and from PASS - so a docs-only close is green with the reason on the record
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
