# US0271: The derivation refuses what G2 refuses: no childless request, no unresolved child, and a no-op where the two-backlog workflow is unenforced

> **Status:** Draft
> **Delivers:** CR0364
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/reference-reconcile.md
> **Epic:** EP0087
> **Points:** 2

## User Story

**As a** consuming project
**I want** the derivation to refuse exactly what G2 refuses
**So that** a request is never closed on evidence the gate itself would reject

## Context

Three guards, each a way the derivation could become a vacuous pass that closes requests it
should not. The childless case is the sharpest: "produced nothing" must never read as "delivered
everything", and it is already the `undecomposed` kind - the two must stay distinct.

## Acceptance Criteria

### AC1: a childless request is never derived

- **Given** a request with no children at all
- **When** detect runs
- **Then** it is not reported as derivable; it remains the `undecomposed` case
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_a_childless_request_is_never_derivable
- **Verified:** yes (2026-07-19)

### AC2: one unresolved child blocks the derivation

- **Given** a request whose children are terminal except one
- **When** detect runs
- **Then** it is not reported as derivable
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_one_unresolved_child_blocks_derivation
- **Verified:** yes (2026-07-19)

### AC3: a dropped child counts as resolved

- **Given** a request whose children are Done except one that is Won't Implement
- **When** detect runs
- **Then** it IS reported as derivable, matching the gate's own definition of resolved
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_a_dropped_child_counts_as_resolved
- **Verified:** yes (2026-07-19)

### AC4: a no-op where the workflow is unenforced

- **Given** a project that does not set `two_backlog.enforce`
- **When** detect runs
- **Then** no request is reported as derivable, so an unenforced project closes requests by
  assertion exactly as before
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k test_unenforced_project_reports_no_derivable_requests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Groomed against the undecomposed_drift sibling and the G2 gate |
