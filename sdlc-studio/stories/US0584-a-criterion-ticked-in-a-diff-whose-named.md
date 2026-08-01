# US0584: A criterion ticked in a diff whose named surface that diff does not touch is flagged, and one whose surface it does touch is not

> **Status:** Review
> **Delivers:** CR0517
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py
> **Epic:** EP0195
> **Points:** 5

## User Story

**As a** maintainer reading a closed unit
**I want** a criterion ticked over a surface the diff never touched flagged at delivery
**So that** a false completion claim is caught where it is still free to fix

## Acceptance Criteria

### AC1: a tick over an untouched surface is flagged

- **Given** a staged diff ticking a criterion whose named surface that diff does not touch
- **When** the lane runs
- **Then** it reports the tick and the surface it names, because a criterion recorded met while the tree disproves it is a false completion claim the close currently accepts
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimTickTests::test_a_tick_over_an_untouched_surface_is_flagged
- **Verified:** yes (2026-08-01)

### AC2: a tick over a changed surface is not flagged

- **Given** a staged diff ticking a criterion whose named surface it does change
- **When** the lane runs
- **Then** it reports nothing, so the check distinguishes a met criterion from an asserted one
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimTickTests::test_a_tick_over_a_changed_surface_passes
- **Verified:** yes (2026-08-01)

### AC3: a criterion naming no surface is reported as unjudgeable, never as passing

- **Given** a ticked criterion whose text names no file, test or command
- **When** the lane runs
- **Then** it reports the criterion as one it cannot judge rather than passing it, because an unanswerable check must not read the same as a satisfied one
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimTickTests::test_an_unjudgeable_criterion_is_named_not_passed
- **Verified:** yes (2026-08-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
