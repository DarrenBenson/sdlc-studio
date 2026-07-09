# US0109: rc-tag readiness checklist enumerated so the tag decision is a checklist read

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0024
> **Persona:** Engineering seat
> **Affects:** templates/workflows/release-gate.md, sdlc-studio/reviews/v4-rc-readiness.md
> **Depends on:** US0106, US0107, US0108

## User Story

**As a** maintainer deciding whether to cut `v4.0.0-rc.1`
**I want** the rc-tag requirements enumerated as a checklist
**So that** cutting the tag is a checklist read (each item green or not), not a judgement call

Delivers CR0198 item 5. The tag cut, freeze lift, and push remain an explicit operator action once the checklist reads green.

## Acceptance Criteria

### AC1: the rc-tag readiness checklist enumerates every gate

- **Given** the v4 rc-readiness record
- **When** it is read
- **Then** it lists each requirement with a checkable state: green portable gate, migration rehearsal done (US0106), EP0014 closed, open-bug count 0, version/CHANGELOG at 4.0.0-rc.1 (US0108)
- **Verify:** file sdlc-studio/reviews/v4-rc-readiness.md
- **Verified:** yes (2026-07-09)

### AC2: the checklist names the open-bug and EP0014 gates explicitly

- **Given** the readiness record
- **When** it is read
- **Then** it names the open-bug-count-0 gate and the EP0014-closed gate (regenerated from the census at write time, not a stale hand-typed number)
- **Verify:** grep "open.bug|EP0014" sdlc-studio/reviews/v4-rc-readiness.md
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0198 item 5 (rc-tag checklist) |
