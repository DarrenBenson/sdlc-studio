# US0527: validate can be pointed at one artefact, so checking a story does not read the whole workspace

> **Status:** Done
> **Delivers:** CR0456
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0180
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** lane wanting to check the one story it just edited
**I want** validate to be pointed at a single artefact
**So that** checking one file does not read the whole workspace

## Acceptance Criteria

### AC1: validate accepts a single artefact and reports only its findings

- **Given** a workspace of many artefacts
- **When** validate is pointed at one
- **Then** it reports that artefact's findings and reads only what that requires
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::ScopedCheckTests::test_a_single_artefact_can_be_checked
- **Verified:** yes (2026-07-28)

### AC2: a scoped run says it was scoped, so its silence is not read as a clean workspace

- **Given** a scoped run that finds nothing
- **When** it reports
- **Then** it states the scope it covered, because 'no findings here' and 'no findings anywhere' are different claims
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::ScopedCheckTests::test_a_scoped_run_states_its_scope
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
