# US0270: reconcile apply derives the request terminal through transition, so every gate and cascade still runs

> **Status:** Draft
> **Delivers:** CR0364
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0087
> **Points:** 3

## User Story

**As an** operator
**I want** `reconcile apply` to close a request whose children are all done
**So that** the backlog corrects itself instead of needing 26 hand transitions

## Context

The transition must go through `transition.transition`, not a direct file write, so the index
cascade, the epic breakdown sync and the telemetry event all still run. It is safe by
construction: the same G2 gate that refuses a premature close passes by definition once every
child is resolved, so apply asserts nothing the gate would not already allow.

## Acceptance Criteria

### AC1: apply derives the request to its successful terminal

- **Given** a CR reported as derivable by detect
- **When** `reconcile apply` runs
- **Then** the CR's status is its type's successful terminal (Complete for a CR, Accepted for an
  RFC, Resolved for an Issue) and its index row agrees
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_apply_derives_the_request_terminal
- **Verified:** yes (2026-07-19)

### AC2: the transition runs through the real path

- **Given** the derivation
- **When** it transitions the request
- **Then** it calls `transition.transition`, so the index row, any parent cascade and the
  telemetry event happen exactly as a hand transition would
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_apply_goes_through_transition
- **Verified:** yes (2026-07-19)

### AC3: applying twice is a no-op

- **Given** a workspace where apply has already derived every derivable request
- **When** detect runs again
- **Then** it reports zero drift of this kind
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_apply_is_idempotent
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Groomed against the undecomposed_drift sibling and the G2 gate |
