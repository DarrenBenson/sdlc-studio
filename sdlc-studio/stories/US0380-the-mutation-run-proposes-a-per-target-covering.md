# US0380: the mutation run proposes a per-target covering command from its own reference scan, zero out-of-selection warnings by construction, a hand --test unchanged

> **Status:** Draft
> **Delivers:** CR0377
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0138
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: given targets and no --test, or a --suggest-test flag, the run prints the derived covering command

- **Given** {{context}}
- **When** {{action}}
- **Then** given targets and no --test, or a --suggest-test flag, the run prints the derived covering command per target (the referencing test files its scan found), with the honest caveat that reference-scan coverage is a heuristic
- **Verify:** {{executable check}}

### AC2: a run executed with the derived command produces zero out-of-selection warnings for its targets, by

- **Given** {{context}}
- **When** {{action}}
- **Then** a run executed with the derived command produces zero out-of-selection warnings for its targets, by construction
- **Verify:** {{executable check}}

### AC3: the hand-supplied --test path is unchanged and remains the default

- **Given** {{context}}
- **When** {{action}}
- **Then** the hand-supplied --test path is unchanged and remains the default
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
