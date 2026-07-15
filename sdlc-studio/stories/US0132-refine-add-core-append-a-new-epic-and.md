# US0132: refine add core: append a new epic and stories to an already-decomposed request, Decomposed-into append-only

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Epic:** EP0036
> **Points:** 3

## User Story

**As an** operator delivering a large request in slices
**I want** `refine add` to append a further epic + stories to an already-decomposed request
**So that** a request whose first epic already shipped (RFC0039, RFC0040) can grow its next slice with the tool, not by hand.

## Acceptance Criteria

### AC1: refine add appends a second epic, Decomposed-into append-only

- **Given** a request already decomposed into one epic
- **When** `refine.refine_add(root, request, epic_title, stories)` runs
- **Then** it creates a new epic + stories, appends the new epic to the request's `Decomposed-into:` (the first epic preserved), and both resolve via `children_of`; reconcile shows no link-asymmetry
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::RefineTests::test_refine_add_appends_a_second_epic_without_losing_the_first
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
