# US1176: The release gate lists a declared non-completing status's failing criteria as unbuilt, and an undeclared one still fails

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0636
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_gate_declared_status.py
> **Epic:** EP0317
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The release gate lists a declared non-completing status's failing criteria as unbuilt, and an undeclared one still fails
**So that** CR0636 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A declared non-completing status lists its failing criteria as unbuilt

- **Given** a project whose `.config.yaml` declares the extended story status `Partially Done` and declares it as not claiming completion, and a story at that status with one failing executable criterion
- **When** the release gate is run
- **Then** the criterion is listed as unbuilt, it is not in the red count, and the gate does not fail on it. Fails on: the criterion counted red, so a part-delivered story fails the release gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_declared_status.py::DeclaredStatusTests::test_declared_non_completing_status_is_unbuilt

### AC2: An undeclared extended status still fails closed

- **Given** the same story at an extended status the project added to its vocabulary but did not declare as non-completing, and again at a misspelt status
- **When** the release gate is run
- **Then** the failing criterion is counted red in both. Fails on: any status the base vocabulary cannot classify dropping out of the red count without a declaration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_declared_status.py::DeclaredStatusTests::test_undeclared_extended_status_fails_closed

### AC3: A status that claims completion cannot be declared out of the count

- **Given** a project that declares `Done`, or another base terminal status, as not claiming completion
- **When** the release gate is run over a Done story with a failing criterion
- **Then** the criterion is still counted red and the gate names the declaration it ignored; the shipped default declares no status, and `reference-config.md` documents the key with that default. Fails on: one config line that takes every finished story's red criteria out of the release gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_declared_status.py::DeclaredStatusTests::test_a_base_terminal_status_cannot_be_declared_non_completing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
