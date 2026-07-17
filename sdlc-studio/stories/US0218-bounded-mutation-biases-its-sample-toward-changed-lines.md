# US0218: bounded mutation biases its sample toward changed lines

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py
> **Epic:** EP0072
> **Points:** 5

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: When --since (or a changed-lines set) is available, mutation prioritises mutants on the changed

- **Given** {{context}}
- **When** {{action}}
- **Then** When --since (or a changed-lines set) is available, mutation prioritises mutants on the changed lines before spending the ceiling on unchanged code; a run that cannot cover the diff within the ceiling says so, naming the diff coverage achieved.
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
