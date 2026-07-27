# US0450: The PRD Target Users section names the registry's Primary, Secondary and Negative personas and points at the registry

> **Status:** Review
> **Delivers:** CR0426
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_persona_coherence.py
> **Epic:** EP0166
> **Points:** 2

## User Story

**As a** reader consulting the top-of-pipeline authority to learn who this product is for
**I want** the PRD's Target Users section to name the registry's declared personas and point at the registry
**So that** the PRD and the persona registry state one design target instead of two contradictory ones

## Acceptance Criteria

### AC1: Target Users names every declared persona with its role

- **Given** the registry declaring a Primary, a Secondary and a Negative persona
- **When** the PRD's Target Users section is read
- **Then** it names each of them with its role and links to `sdlc-studio/personas/index.md`, and no longer designates `personas.md` as the authority
- **Verify:** pytest tools/tests/test_persona_coherence.py::PrdTargetUsersTests::test_target_users_names_every_declared_persona
- **Verified:** yes (2026-07-27)

### AC2: the expectation is derived from the registry, so a change on either side fails the check

- **Given** a registry entry added, renamed or removed
- **When** the check runs
- **Then** it fails until the PRD names the changed set, because the expected names are read from `personas/index.md` at check time and never hardcoded in the test
- **Verify:** pytest tools/tests/test_persona_coherence.py::PrdTargetUsersTests::test_expected_names_are_derived_from_the_registry_not_hardcoded
- **Verified:** yes (2026-07-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: user story and acceptance criteria authored against the slice |
