# US0564: A unit typed as a repair requires mutation evidence over its own changed lines before it can reach a terminal status

> **Status:** Ready
> **Delivers:** CR0501
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0191
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer closing a batch of repairs
**I want** a repair to carry mutation evidence over the lines it actually changed before it can reach a terminal status
**So that** a fix held only by a test its own author wrote cannot reach Fixed, which is how nine self-reviewed repairs shipped green in RUN-01KYNKDP

## Acceptance Criteria

### AC1: a repair-typed unit reaching terminal without mutation evidence is refused

- **Given** a bug at `Open` whose changed surface is a Python module, and no mutation record for it
- **When** `transition.py set --id <bug> --status Fixed` runs
- **Then** it exits non-zero naming the missing mutation evidence and the command that produces it, in the same refusal shape the existing verification-depth demand already uses, because a repair is the least-reviewed code in a sprint and this is the point at which the claim is made
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RepairMutationGateTests::test_a_repair_without_mutation_evidence_is_refused

### AC2: the mutated surface is the unit's own changed lines, not its whole Affects

- **Given** a repair whose `Affects` names a 2,000-line module in which it changed nine lines
- **When** the mutation evidence is derived for that unit
- **Then** the mutant set is generated over those nine changed lines only, established from the unit's diff against the run's base ref, so the gate stays affordable and cannot be passed by mutants landing in code the repair never touched
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::ChangedLineScopeTests::test_mutants_are_scoped_to_the_units_changed_lines

### AC3: the evidence is re-read from the record, never accepted from the caller

- **Given** a caller that asserts mutation passed by passing a flag or by writing a claim into the artefact prose
- **When** the transition gate evaluates the unit
- **Then** the claim is ignored and the gate reads the recorded mutation run for that unit id and that base ref, refusing when no such record exists, because a gate that trusts the thing it is gating checks nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RepairMutationGateTests::test_an_asserted_pass_without_a_record_is_refused

### AC4: a record that does not match the unit's current surface is stale, not green

- **Given** a mutation record for a unit, and a subsequent edit that changes a line the record did not cover
- **When** the transition gate runs
- **Then** it refuses as STALE, naming the uncovered line and distinguishing that state from "no record at all", so a passing run cannot be banked and spent against later changes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::RepairMutationGateTests::test_a_record_predating_the_current_surface_is_stale

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
