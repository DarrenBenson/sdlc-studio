# US0565: The gate is the SURVIVOR count over those lines, and a surviving mutant refuses the transition naming the mutant and its line

> **Status:** Draft
> **Delivers:** CR0501
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Epic:** EP0191
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer relying on the repair gate
**I want** the gate to be the survivor count over the changed lines, not the fact that a mutation run happened
**So that** running mutation and ignoring the result cannot pass, which is the failure mode a mere run-it requirement produces

## Acceptance Criteria

### AC1: a completed run carrying a survivor refuses the transition

- **Given** a repair with a mutation record whose run completed successfully and reports 12 mutants applied, 11 killed and 1 survived
- **When** the transition to a terminal status runs
- **Then** it exits non-zero on the SURVIVOR count, not on the run's own exit status, because a mutation run that completes is evidence a run happened and says nothing about whether the tests can fail
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorGateTests::test_a_completed_run_with_one_survivor_refuses

### AC2: the refusal names the surviving mutant and its line

- **Given** the refusal from AC1
- **When** its output is read
- **Then** it names each surviving mutant by the file, the line number and the applied mutation, so the author is told which assertion is missing rather than that a number was too high
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorGateTests::test_the_refusal_names_each_survivor_with_its_file_line_and_mutation

### AC3: zero survivors over a non-empty mutant set passes

- **Given** a repair whose record reports 12 mutants applied and 12 killed
- **When** the transition runs
- **Then** it proceeds, and the record's mutant count and base ref are stamped on the unit so the pass is auditable after the fact
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorGateTests::test_zero_survivors_over_a_non_empty_set_passes

### AC4: an empty mutant set is not a pass

- **Given** a repair whose record reports 0 mutants applied, whether because generation found no mutatable construct or because the run errored before applying any
- **When** the transition runs
- **Then** it refuses rather than passing on a zero survivor count, distinguishing "nothing to mutate" from "nothing survived", because `survivors == 0` over an empty set is the vacuous green this gate exists to refuse. The legitimate no-surface case is US0566's recorded exemption, not this silent one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorGateTests::test_an_empty_mutant_set_is_refused_not_passed

### AC5: bytecode staleness cannot manufacture a kill

- **Given** a mutation run over a module whose `__pycache__` holds bytecode compiled from the unmutated source
- **When** the run applies a same-length mutant and executes the suite
- **Then** the run purges the cached bytecode and executes with `python3 -B`, and asserts the patch changed the file before executing, so a cached `.pyc` cannot report a survivor as killed or a kill as survived
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::BytecodeIsolationTests::test_a_stale_pyc_cannot_decide_a_mutants_verdict

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
