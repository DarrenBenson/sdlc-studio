# EP0004: Testing Pipeline

> **Status:** Ready
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

## Summary

Produce test specifications, generate executable tests from them, and stand up a
containerised test environment. In generate mode this is the validation engine:
tests run against the existing implementation to prove the extracted spec is true.

**PRD Reference:** [Validation Requirement](../prd.md#10-quality-assessment)

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

- [ ] Test specs define cases and fixtures, with epic-scoped coverage handled.
- [ ] Generated tests are executable in the project's framework.
- [ ] Generate-mode specs are not "Done" until tests pass against the implementation.
- [ ] Test environment is reproducible.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| EP0002 | Epic | Ready | Darren Benson |
| EP0003 | Epic | Ready | Darren Benson |

## Sizing

**Estimated Story Count:** 4

## Story Breakdown

- [ ] US: Test spec creation
- [ ] US: Test automation (executable tests)
- [ ] US: Test environment setup
- [ ] US: Generate-mode validation gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
