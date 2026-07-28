# US0506: A report attributes suite time and test count to the module each test covers, so the expensive areas are visible

> **Status:** Review
> **Delivers:** CR0455
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests, tools/test_census.py, tools/tests/test_test_census.py
> **Epic:** EP0177
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer deciding where the suite's cost is going
**I want** suite time and test count attributed to the module each test covers
**So that** the expensive areas are visible rather than guessed, which is the precondition for pruning anything

## Acceptance Criteria

### AC1: the report attributes time and count per covered module

- **Given** a completed suite run
- **When** the census runs
- **Then** it reports per module the number of tests and the time they took, ordered by cost
- **Verify:** pytest tools/tests/test_test_census.py::CensusTests::test_time_and_count_are_attributed_per_module

### AC2: a test covering no resolvable module is reported, not dropped

- **Given** a test the census cannot attribute
- **When** it runs
- **Then** that test is named as unattributed rather than silently excluded, so the total stays honest
- **Verify:** pytest tools/tests/test_test_census.py::CensusTests::test_an_unattributable_test_is_named_not_dropped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
