# US1237: A project sets the CI wait timeout and the rerun limit in config, with the defaults documented

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0697
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_ci_wait_config.py, tools/check_budgets.py, changelog.d/US1237.md
> **Epic:** EP0340
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A project sets the CI wait timeout and the rerun limit in config, with the defaults documented
**So that** CR0697 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The defaults carry a wait timeout and a rerun limit of one

- **Given** a project with no override, and one whose config sets both keys
- **When** the CI wait timeout and the rerun limit are read through the shipped config loader
- **Then** the first project gets the timeout `config-defaults.yaml` states and a rerun limit of one, and the second gets its own two values. Fails on: a key documented and absent from the defaults, or a project's override ignored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ci_wait_config.py::CiWaitConfigTests::test_the_defaults_and_a_project_override_are_read

### AC2: The config reference documents both keys with the defaults the file holds

- **Given** `reference-config.md` and `config-defaults.yaml`
- **When** the reference's entry for the two keys is read
- **Then** it names each key by the spelling the defaults file uses, states the same default for each, and says what the timeout bounds and what the limit counts. Fails on: a default in the reference that differs from the file, or a key name the code does not read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ci_wait_config.py::CiWaitConfigTests::test_the_reference_states_the_defaults_the_file_holds

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
