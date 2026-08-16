# US0650: help and reference-scripts point at the contract reporter instead of restating any contract

> **Status:** Ready
> **Delivers:** CR0535
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/help/, tools/tests/test_check_spec_claims.py
> **Epic:** EP0210
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** help and reference-scripts point at the contract reporter instead of restating any contract
**So that** CR0535 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: no help page restates a contract the reporter derives

- **Given** the shipped help/ and reference-scripts.md
- **When** they are swept for restated contracts - required flags, accepted vocabularies, field shapes
- **Then** none restates one; each points at the reporter instead. A doc that repeats a guard is a second source of truth that nothing reddens when it drifts
- **Mutant:** leave one page restating its verb's flags - it is correct today and silently wrong after the next guard change
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ContractsAreNotRestatedTests::test_no_help_page_restates_a_derived_contract

### AC2: the pointer resolves to a runnable command

- **Given** a help page pointing at the reporter
- **When** the pointer is followed
- **Then** it names a command that runs and answers - a pointer to something a reader cannot invoke is a restatement with extra steps
- **Mutant:** point at a prose section instead - the reader is redirected rather than answered
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ContractsAreNotRestatedTests::test_the_pointer_names_a_runnable_command

### AC3: a page that must restate says why

- **Given** a page where restating is genuinely right
- **When** the sweep runs
- **Then** it carries a recorded reason and is exempted BY NAME - an exemption nobody can count is indistinguishable from an omission
- **Mutant:** exempt by pattern - the exempt set grows silently and the sweep stops meaning anything
- **Verify:** pytest tools/tests/test_check_spec_claims.py::ContractsAreNotRestatedTests::test_an_exemption_is_named_and_reasoned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
