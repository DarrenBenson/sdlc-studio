# US0129: refine core: create an epic and stories from a request with links wired

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Epic:** EP0035
> **Points:** 5

## User Story

**As an** operator with a request in the Discovery backlog
**I want** one command that turns it into an epic and stories with the links wired
**So that** I stop hand-decomposing (CR0271 -> EP0033) and the two-backlog gates can verify the result.

## Acceptance Criteria

### AC1: refine creates an epic + stories and wires the links both ways

- **Given** a refinable request (an RFC/CR, not already decomposed) and a story breakdown (title + points)
- **When** `refine.refine(root, request, epic_title, stories)` runs
- **Then** it creates the epic (T-shirt sized from the point total, `Parent:` the request) and each story under it, writes the request's `Decomposed-into:` and rolls the epic's `Derived Point Total`; the chain resolves both ways (no link-asymmetry) and the request is no longer undecomposed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::RefineTests
- **Verified:** yes (2026-07-15)

### AC2: refine validates before minting - a bad breakdown leaves the backlog untouched

- **Given** a non-request, an already-decomposed request, an off-scale story point, or an empty breakdown
- **When** refine is asked to decompose it
- **Then** it refuses with a clear reason and mints nothing (the request stays undecomposed)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::RefineTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
