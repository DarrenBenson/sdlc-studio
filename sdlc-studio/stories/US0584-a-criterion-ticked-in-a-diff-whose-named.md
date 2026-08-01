# US0584: A criterion ticked in a diff whose named surface that diff does not touch is flagged, and one whose surface it does touch is not

> **Status:** Draft
> **Delivers:** CR0517
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py
> **Epic:** EP0195
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a tick over an untouched surface is flagged

- **Given** a staged diff ticking a criterion whose named surface that diff does not touch
- **When** the lane runs
- **Then** it reports the tick and the surface it names, because a criterion recorded met while the tree disproves it is a false completion claim the close currently accepts
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimTickTests::test_a_tick_over_an_untouched_surface_is_flagged

### AC2: a tick over a changed surface is not flagged

- **Given** a staged diff ticking a criterion whose named surface it does change
- **When** the lane runs
- **Then** it reports nothing, so the check distinguishes a met criterion from an asserted one
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimTickTests::test_a_tick_over_a_changed_surface_passes

### AC3: a criterion naming no surface is reported as unjudgeable, never as passing

- **Given** a ticked criterion whose text names no file, test or command
- **When** the lane runs
- **Then** it reports the criterion as one it cannot judge rather than passing it, because an unanswerable check must not read the same as a satisfied one
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ClaimTickTests::test_an_unjudgeable_criterion_is_named_not_passed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
