# US0563: The shipped lifecycle states the batch-boundary cadence: doctrine, definition-of-done and help, so a consuming project inherits the placement

> **Status:** Done
> **Delivers:** CR0500
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/help/sprint.md
> **Epic:** EP0190
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** a team adopting this lifecycle in another project
**I want** the shipped doctrine, Definition of Done and help to state the batch-boundary cadence
**So that** the project inherits the PLACEMENT of the review and not merely a lesson saying it matters

## Acceptance Criteria

### AC1: The shipped doctrine states the batch-boundary review cadence, so a consuming project inherits the PLACEMENT and not only the lesson

- **Verify:** grep "delivery batch boundary, not at the close" .claude/skills/sdlc-studio/reference-doctrine.md
- **Verified:** yes (2026-07-29)

### AC2: The shipped Definition of Done carries the batch-review clause in the same checkable form as its existing clauses

- **Verify:** grep "independent review has covered THIS batch" .claude/skills/sdlc-studio/templates/core/definition-of-done.md
- **Verified:** yes (2026-07-29)

### AC3: `help/sprint.md` documents `review-batch` in runnable invocation form

- **Verify:** manual - retired by US0918: `sprint.py review-batch` is retired and no longer documented
- **Verified:** manual (2026-09-26) - retired, superseded by US0918

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-26 | US0918 | AC3 retired in the D0259 pattern: `sprint.py review-batch` is retired and no longer documented |
