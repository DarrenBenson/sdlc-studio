# US0131: refine closes the loop: request status + amigo consult for open questions

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Epic:** EP0035
> **Points:** 2

## User Story

**As an** operator finishing a refine
**I want** the request moved to its working status and open questions raised for the amigos
**So that** the backlog shows the request as being delivered and the Three Amigos settle the unknowns before building.

## Acceptance Criteria

### AC1: refine moves the request to its working status

- **Given** an Approved CR being decomposed
- **When** `refine` wires the epic and stories
- **Then** the CR moves to In Progress (it is now delivered via its children, and reaches terminal only by derivation, G2)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::RefineTests::test_refine_moves_the_request_to_its_working_status
- **Verified:** yes (2026-07-15)

### AC2: refine surfaces open questions for the Three-Amigos consult

- **Given** open questions passed to refine
- **When** it completes
- **Then** it returns the non-empty questions and names the amigo roles (engineering, product, qa) to settle them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::RefineTests::test_refine_surfaces_open_questions_for_the_amigos
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
