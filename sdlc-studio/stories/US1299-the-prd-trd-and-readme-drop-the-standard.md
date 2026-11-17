# US1299: The PRD, TRD and README drop the standard-library-only claim, the TRD gains the ADR and the notes name the break

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0731
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md, README.md, docs/known-issues.md, tools/tests/test_lean_trd_refresh.py
> **Epic:** EP0368
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The PRD, TRD and README drop the standard-library-only claim, the TRD gains the ADR and the notes name the break
**So that** CR0731 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: No spec page claims a standard-library-only runtime

- **Given** `sdlc-studio/prd.md`, `sdlc-studio/trd.md` and `README.md`
- **When** their tech stack, component, constraint and requirement statements are read
- **Then** none says the scripts are standard library only, pure stdlib, or free of third-party packages, none says PyYAML is used when present or degrades to defaults when absent, and each names PyYAML as a required dependency. Fails on: the PRD's 'stdlib only' tech stack line, or the TRD's constraint that rules out a required third-party dependency, as they stand at grooming
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdRequiredPyYamlTests::test_no_spec_page_claims_a_standard_library_only_runtime

### AC2: The TRD records the ruling as an ADR and carries the threat row

- **Given** `sdlc-studio/trd.md`
- **When** its ADRs and its threat model table are read
- **Then** one ADR with Status Accepted cites D0505 and RFC0066 and states that the installer and the prerequisite check refuse without PyYAML; the threat model has a row for a missing or tampered PyYAML with its mitigation; and the supply-chain row no longer says there is no third-party package to compromise. Fails on: a TRD with no ADR citing D0505, or a threat table whose supply-chain row still reads pure stdlib
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdRequiredPyYamlTests::test_the_trd_records_the_pyyaml_ruling_and_its_threat_row

### AC3: The notes for the next version name the break

- **Given** this unit's changelog fragment, from which the next release's notes are composed
- **When** it is read
- **Then** it is filed under Breaking, says PyYAML is now required, says a machine without it is refused at install and at the gate, and gives the command that installs it. Fails on: the requirement filed as an ordinary change, or a fragment that does not say what a machine without PyYAML must do

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
