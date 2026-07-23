# BG0274: artifact.retitle write phase is a sequence of independent writes with no rollback, so a fault mid-loop (e.g. an unreadable reference file) leaves the file renamed and index updated but inbound references half-rewritten

> **Status:** Open
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py
> **Severity:** Medium
> **Points:** 5

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |

## Acceptance Criteria

- [ ] the retitle either completes atomically or rolls back, never leaving surfaces inconsistent
- **Given** a reference file becomes unreadable partway through a retitle's inbound-rewrite loop
- **Then** the retitle either completes atomically or rolls back, never leaving surfaces inconsistent
- **Verify:** manual
