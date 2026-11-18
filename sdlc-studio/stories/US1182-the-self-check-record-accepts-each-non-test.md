# US1182: The self-check record accepts each non-test file in the unit's Affects as an optional surface and still requires the rest

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0652
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py
> **Epic:** EP0321
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The self-check record accepts each non-test file in the unit's Affects as an optional surface and still requires the rest
**So that** CR0652 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A claim filed under a non-test file the unit's Affects declares is accepted

- **Given** a unit whose Affects declares a prose file (AGENTS.md), a reference page and its changelog fragment, and a claims file whose claims name the commit message, the fragment and AGENTS.md by its path
- **When** `critic.py self-check record --unit <id> --author <name> --claims <file> --mutants <file>` runs
- **Then** the row is written and its claim count includes the claims filed under AGENTS.md. Fails on: the refusal the tree gives today, that the claim names a surface the self-check does not name
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_a_claim_under_a_declared_non_test_file_is_accepted

### AC2: A file outside the Affects, or a declared test file, is still refused as a surface

- **Given** the same unit, and a claims file naming as its surface a file the Affects does not declare, then one naming a test file the Affects does declare
- **When** the record command runs on each
- **Then** each is refused with the surface named and no row is written; the same claims refiled under the commit message are accepted. Fails on: any path at all being taken as a surface, or a test file read as prose that makes claims
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_an_undeclared_file_or_a_test_file_is_refused_as_a_surface

### AC3: The commit message and each fragment stay required and the Affects files stay optional

- **Given** the same unit
- **When** the author self-check section is printed and three claims files are recorded: one covering only the commit message and the fragment, one covering AGENTS.md but not the commit message, one covering AGENTS.md but not the fragment
- **Then** the section lists each declared non-test file as a named optional surface; the first file is accepted and the second and third are each refused naming the required surface they skip. Fails on: a declared prose file made required, or a claim under one standing in for the commit message or the fragment
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_the_required_surfaces_stay_required_beside_the_optional_files

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
