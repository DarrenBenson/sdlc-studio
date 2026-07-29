# US0557: A batch invocation missing a required argument is refused once before any unit is written, naming every argument the command needs

> **Status:** Review
> **Delivers:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0189
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an agent driving the critic verbs for the first time
**I want** a missing required argument refused once, up front, naming everything the command needs
**So that** an argument learned by failing costs one refusal rather than nineteen wasted spawns

## Acceptance Criteria

### AC1: the refusal comes before any unit is written

- **Given** a batch invocation missing a required argument
- **When** it runs against a batch of several units
- **Then** it refuses before writing any unit, and no artefact in the batch has changed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ArgumentCompletenessTests::test_a_missing_argument_refuses_before_any_unit_is_written
- **Verified:** yes (2026-07-29)

### AC2: the refusal names every argument the command needs, not only the first missing one

- **Given** an invocation missing two required arguments
- **When** it is refused
- **Then** both are named in that one message, so a second round-trip is not needed to discover the second
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ArgumentCompletenessTests::test_the_refusal_names_every_missing_argument
- **Verified:** yes (2026-07-29)

### AC3: the message the refusal prints matches the argument the parser actually reads

- **Given** each critic verb
- **When** its refusal message names an argument
- **Then** that name is the one the parser accepts, so a message cannot send a caller to a flag the command does not have
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ArgumentCompletenessTests::test_every_named_argument_is_one_the_parser_accepts
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-29 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
