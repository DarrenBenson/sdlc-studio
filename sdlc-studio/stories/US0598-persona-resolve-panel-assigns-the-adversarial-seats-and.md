# US0598: persona_resolve panel assigns the adversarial seats and the SIGNING seat disjointly, and the assignment is recorded on the run

> **Status:** Ready
> **Delivers:** CR0514
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py
> **Epic:** EP0198
> **Points:** 5

## User Story

**As a** maintainer of the two-role gate
**I want** the panel's adversarial seats and its signing seat assigned disjointly and recorded on the run
**So that** a panel sign-off cannot become a self-review with more steps

## Acceptance Criteria

### AC1: the adversarial seats and the signing seat are disjoint

- **Given** a unit whose panel is resolved by `persona_resolve.py panel`
- **When** the assignment is read
- **Then** no seat appears both as an adversarial reviewer and as the signer, because a seat that reviewed its own evidence is the merged role the two-role gate exists to prevent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py::PanelAssignmentTests::test_the_signing_seat_is_disjoint_from_the_adversarial_seats

### AC2: the assignment is recorded on the run, not recomputed at sign-off

- **Given** a run whose panel has been assigned
- **When** the sign-off is later recorded
- **Then** it reads the assignment from the run state rather than resolving again, so a seat cannot be re-rolled until it lands on one that suits the answer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py::PanelAssignmentTests::test_the_assignment_is_read_from_the_run_not_recomputed

### AC3: a project with too few seats is refused, not silently narrowed

- **Given** a project whose seat cards cannot supply both roles disjointly
- **When** a panel is requested
- **Then** it is refused naming what is missing, because silently reusing a seat is exactly the failure this story prevents
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py::PanelAssignmentTests::test_too_few_seats_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
