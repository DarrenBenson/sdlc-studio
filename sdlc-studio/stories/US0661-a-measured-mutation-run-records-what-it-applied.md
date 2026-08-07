# US0661: A measured mutation run records what it applied, attributed to a unit, so the gate is satisfiable by measurement rather than only by self-report

> **Status:** Ready
> **Delivers:** CR0537
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0212
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A measured mutation run records what it applied, attributed to a unit, so the gate is satisfiable by measurement rather than only by self-report
**So that** CR0537 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: a measured run satisfies the gate

- **Given** a repair whose only evidence is a real `mutation.py run` over its changed lines with
  every mutant killed, and no `register` claim at all, under `review.mutation_evidence: block`
- **When** `transition.py set --id BG0001 --status Fixed` runs
- **Then** it exits 0 - because today `append_ledger` reduces a measured run's per-mutant records
  to counts and discards them, so the strongest evidence available reads as NO evidence and only
  the author's own typed claim opens the gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_a_measured_run_satisfies_the_gate

### AC2: a ledger that contradicts itself refuses in every mode, `off` included

- **Given** a mutant registered `killed` at a file and line, and a measured run recording
  `survived` at that same file and line under the same content hash, with
  `review.mutation_evidence: off`
- **When** the terminal transition runs
- **Then** it REFUSES, naming both records and the fact that they contradict - this is not a
  quality bar being applied under `off`, it is the instrument lying about itself, and every
  figure derived from a false verdict is wrong
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceLaneCLITests::test_a_recorded_kill_shown_to_survive_refuses_even_when_off

### AC3: a registered mutant records the line the refusal quotes

- **Given** `mutation.py register --unit BG0001 --target src/thing.py --line 2 ...`
- **When** the ledger is read back and a refusal is composed
- **Then** the record carries the line and the refusal quotes `src/thing.py:2` rather than
  `src/thing.py:?` - today no shipped verb can record a line, so every test asserting one passes
  on a fixture the tool itself could never produce
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::RegisteredLineTests::test_register_records_the_line_the_refusal_quotes

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | drop the per-mutant list from a measured entry in mutation.py, which is today's code | a measured run satisfies the gate |
| AC2 | change transition.py to gate the contradiction check behind the mode being other than off | a ledger that contradicts itself refuses in every mode, `off` included |
| AC3 | change mutation.py to accept --line and drop it before writing the record | a registered mutant records the line the refusal quotes |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
