# US0514: A bug reaching a terminal status with no acceptance-criteria section is refused, as a story reaching Done already is

> **Status:** Done
> **Delivers:** CR0459
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0178
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reader taking a bug at Fixed to mean its fix was specified
**I want** a bug reaching a terminal status with no acceptance criteria to be refused, as a story reaching Done already is
**So that** the artefact graph can speak for the code, which it cannot for a unit with no criterion

## Acceptance Criteria

### AC1: a bug reaching a terminal status with no criteria is refused

- **Given** a bug carrying no acceptance-criteria section
- **When** it is transitioned to a terminal status
- **Then** the transition is refused, naming what is missing, exactly as a story reaching Done is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::BugCriteriaTests::test_a_terminal_bug_with_no_criteria_is_refused
- **Verified:** yes (2026-07-28)

### AC2: the rule is derived from the type's own terminal set, not a list of statuses

- **Given** a project whose bug vocabulary adds a terminal status
- **When** that status is used
- **Then** the rule covers it without editing the checker, because the terminal set comes from the vocabulary
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::BugCriteriaTests::test_the_terminal_set_is_derived_not_enumerated
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
