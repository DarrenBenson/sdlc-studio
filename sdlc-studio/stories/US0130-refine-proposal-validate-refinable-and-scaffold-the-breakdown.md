# US0130: refine proposal: validate refinable and scaffold the breakdown

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Epic:** EP0035
> **Points:** 3

## User Story

**As an** operator about to decompose a request
**I want** `refine show` to surface the request's content and confirm it's refinable
**So that** I can propose a good breakdown, and know `refine apply` will accept the same request.

## Acceptance Criteria

### AC1: refine show gathers the request's content and shares apply's refusals

- **Given** a refinable request
- **When** `refine.refinable(root, request)` runs
- **Then** it returns the request's type, summary and impact/design (and refuses a non-request or an already-decomposed request with the same reasons `apply` gives, so show and apply agree on refinable)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::RefineTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
