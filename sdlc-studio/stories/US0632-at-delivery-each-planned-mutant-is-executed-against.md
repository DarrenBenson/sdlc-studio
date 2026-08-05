# US0632: at delivery each planned mutant is EXECUTED against the shipped test and its death recorded

> **Status:** Ready
> **Delivers:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Epic:** EP0207
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer delivering a unit whose test plan was reviewed
**I want** every planned mutant applied to the shipped test and its death recorded
**So that** the plan is evidence rather than paperwork - a plan written and never checked is the same defect one level up

## Acceptance Criteria

### AC1: every planned mutant is executed, and an unexecuted row is not a pass

- **Given** a unit whose reviewed test plan carries four mutant rows, of which one is never applied
- **When** `mutation.py run --story <id> --from-plan` runs
- **Then** the unexecuted row is reported as `not-run` and the unit does not read as evidenced, because a plan whose rows are optional is a plan that measures nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::FromPlanTests::test_an_unexecuted_planned_mutant_is_not_a_pass
- **Caller:** `mutation.py run --from-plan`, reached by `transition.py set --status Done|Fixed` via US0564's gate
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - treating `not-run` as killed must turn this test red
- **Verified:** no

### AC2: a surviving planned mutant refuses the terminal transition, naming the mutant and its line

- **Given** a planned mutant that is applied and whose criterion's `Verify:` line still passes
- **When** the terminal transition is attempted
- **Then** it is refused, naming the mutant, its file and its line, and naming the criterion whose test failed to notice - the finding is about the test, so the message must point at the test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::FromPlanTests::test_a_survivor_refuses_the_transition_and_names_the_criterion
- **Caller:** `transition.py set`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - downgrading a survivor to a warning must turn this test red
- **Verified:** no

### AC3: execution is sound against the two ways a mutation run lies

- **Given** a mutant whose replacement is the same length as the original, and an anchor string occurring more than once in the target file
- **When** the run applies it
- **Then** bytecode is purged and the child runs with bytecode writing disabled so a cached module cannot report a false survival, the anchor is asserted unique before patching so the wrong function cannot be edited, and the source is restored byte-identical afterwards with that restoration asserted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::FromPlanTests::test_a_cached_module_and_an_ambiguous_anchor_are_both_refused
- **Caller:** `mutation.py run --from-plan`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - dropping either the cache purge or the uniqueness assertion must turn this test red
- **Verified:** no

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | sdlc-studio | Groomed: criteria authored against the `mutation.py --from-plan` slice; AC3 pins the two recorded false-survival scars |
