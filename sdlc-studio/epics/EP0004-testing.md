# EP0004: Testing Pipeline

> **Status:** Done
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --


> **Founding epic - closed 2026-07-09.** Every capability below is delivered in the shipped skill (v4.0.0-rc.1); the suite (1455 tests) and the working `/sdlc-studio` commands demonstrate it. The unlinked `US:` breakdown items are early placeholder stubs from before stories were individually tracked - complete in the implementation, not as separate story artefacts. Closed for status hygiene; no capability is outstanding.

## Summary

Produce test specifications, generate executable tests from them, and stand up a
containerised test environment. In generate mode this is the validation engine:
tests run against the existing implementation to prove the extracted spec is true.

**PRD Reference:** [Feature Inventory](../prd.md#3-feature-inventory)

## Scope

### In Scope

- `test-spec` - consolidated plan + cases + fixtures (incl. epic-scoped coverage).
- `test-automation` - generate executable test code.
- `test-env` - containerised environment setup.

### Out of Scope

- Executable AC verification of a single story (`verify_ac`, EP0005).

### Affected Personas

- **Consuming-project Developer:** validates extracted specs against their code.
- **AI Agent:** generates and runs the tests.

## Acceptance Criteria (Epic Level)

- [x] Test specs define cases and fixtures, with epic-scoped coverage handled.
- [x] Generated tests are executable in the project's framework.
- [x] Generate-mode specs are not "Done" until tests pass against the implementation.
- [x] Test environment is reproducible.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| EP0002 | Epic | Ready | Darren Benson |
| EP0003 | Epic | Ready | Darren Benson |

## Sizing

**Estimated Story Count:** 4

## Story Breakdown

- [x] US: Test spec creation
- [x] US: Test automation (executable tests)
- [x] US: Test environment setup
- [x] US: Generate-mode validation gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
