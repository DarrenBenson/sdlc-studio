# US1284: ADR-006 states the strength of its five-run evidence, names bad-plan propagation, and its instance count is tested

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0724
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Epic:** EP0362
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** ADR-006 states the strength of its five-run evidence, names bad-plan propagation, and its instance count is tested
**So that** CR0724 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: ADR-006's Context states how far its five-run evidence reaches

- **Given** ADR-006 in `sdlc-studio/trd.md`, D0014 in `sdlc-studio/decisions.md` and `docs/benchmarks/2026-07-08-n5-run.md`
- **When** the ADR's Context is read
- **Then** it says the benchmark ran five times per cell and that the difference in escapes is reportable but below conventional significance, and its run count and escape figures are the ones D0014 and the write-up give. Fails on: a Context that presents the five-run result as a settled measurement, or a figure that differs from the write-up's
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdAdr006Tests::test_adr_006_states_the_strength_of_its_evidence

### AC2: ADR-006's Consequences name bad-plan propagation as a negative

- **Given** ADR-006's Consequences
- **When** its Negative bullets are read
- **Then** there are at least two: over-firing, and the mandated arm's own failure mode recorded in D0014, a bad plan that propagates because the critic approves against the wrong oracle. Fails on: a Consequences list whose only negative is over-firing
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdAdr006Tests::test_adr_006_names_bad_plan_propagation_as_a_negative

### AC3: The Key Decisions bullet counts the instances it lists

- **Given** the Key Decisions bullet for ADR-006, and a copy of it with the count changed
- **When** the stated number of instances is compared with the ADR ids listed after it
- **Then** the two are equal in the TRD, and the test fails on the changed copy. Fails on: the bullet at grooming, which says four instances and lists three
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdAdr006Tests::test_the_adr_006_instance_count_equals_the_adrs_listed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
