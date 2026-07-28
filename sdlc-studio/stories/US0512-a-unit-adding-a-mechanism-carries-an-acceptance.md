# US0512: A unit adding a mechanism carries an acceptance criterion naming the caller that consumes it

> **Status:** Review
> **Delivers:** CR0461
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/../templates/core/story.md, tools/tests/test_doc_claims.py
> **Epic:** EP0178
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** author writing a criterion for a mechanism
**I want** the criterion to name the caller that consumes the mechanism, not only the function's own behaviour
**So that** a mechanism that reaches nothing is caught while it is being written, not four review rounds later

## Acceptance Criteria

### AC1: a mechanism unit with no criterion naming a caller is reported

- **Given** a unit that adds a mechanism and whose criteria describe only the function's behaviour
- **When** the check runs
- **Then** it reports the unit, naming the criterion that describes a function with no consumer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerNamedTests::test_a_mechanism_with_no_named_caller_is_reported
- **Verified:** yes (2026-07-28)

### AC2: a criterion naming a caller satisfies it, and the caller must exist

- **Given** a criterion naming a hook, lane or command as the consumer
- **When** the check runs
- **Then** the unit passes only when the named caller resolves to something in the tree, so naming a caller that does not exist is not a way past it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerNamedTests::test_the_named_caller_must_resolve
- **Verified:** yes (2026-07-28)

### AC3: the story template asks for it where the author is looking

- **Given** the shipped story template
- **When** an author writes a criterion
- **Then** the template asks for the consuming caller at the point the criterion is written, rather than leaving it to a lesson the author would have to recall
- **Verify:** pytest tools/tests/test_doc_claims.py::CallerNamedTests::test_the_template_asks_for_the_caller
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
