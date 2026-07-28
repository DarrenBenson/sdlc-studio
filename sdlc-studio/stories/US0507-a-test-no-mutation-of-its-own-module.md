# US0507: A test no mutation of its own module can kill is reported as a removal candidate, and removing one records what it no longer protects

> **Status:** Review
> **Delivers:** CR0455
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, tools/tests, tools/test_census.py, tools/tests/test_test_census.py
> **Epic:** EP0177
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer pruning a suite that only ever grows
**I want** a test no mutation of its own module can kill reported as a removal candidate
**So that** pruning is driven by evidence the test protects nothing, not by how slow it is

## Acceptance Criteria

### AC1: a test no mutation can kill is a removal candidate

- **Given** a module whose mutants are all killed by other tests
- **When** the census runs with mutation evidence
- **Then** the test that killed nothing is reported as a candidate, with the mutants it failed to catch named
- **Verify:** pytest tools/tests/test_test_census.py::PruneCandidateTests::test_a_test_no_mutation_kills_is_a_candidate

### AC2: removing a test records what it no longer protects

- **Given** an approved removal
- **When** it is recorded
- **Then** the record states what the test asserted and why that is now covered elsewhere or no longer true, so pruning cannot quietly become coverage loss
- **Verify:** pytest tools/tests/test_test_census.py::PruneCandidateTests::test_a_removal_records_what_it_no_longer_protects

## Scope note (added at review)

**This unit ships the CONSUMER only.** `prune_candidates` refuses evidence whose killed mutants
carry no `killed_by`, and `mutation.py` - this repository's only mutation-evidence producer - does
not emit that key, so `test_census.py candidates` takes the refusal branch against every real
report available today. The refusal is loud rather than a false green, and the module says so, but
the capability is not reachable in production until the producer records which test killed each
mutant. That half is filed as BG0357.

Recorded here rather than left implicit because it is this sprint's own headline lesson applied to
this sprint: ship the wiring in the same unit as the mechanism, or name the caller that is missing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
| 2026-07-28 | Claude Fable 5 | Scope narrowed to consumer-only at review; producer half filed as BG0357 |
