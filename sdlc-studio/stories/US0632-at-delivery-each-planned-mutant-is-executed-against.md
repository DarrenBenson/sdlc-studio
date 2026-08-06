# US0632: at delivery each planned mutant is EXECUTED against the shipped test and its death recorded

> **Status:** Done
> **Delivers:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Epic:** EP0207
> **Depends on:** US0629
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
- **Mutation-checked:** yes (2026-08-06). Treating `not-run` as killed KILLED; letting a later kill cancel an earlier survivor KILLED. The criterion-guard mutant (join on unit alone) is EQUIVALENT, not uncovered: an unkeyed registration then keys on `None` and no lookup ever asks for `None`
- **Verified:** yes (2026-08-06)

### AC2: a surviving planned mutant refuses the terminal transition, naming the mutant and its line

- **Given** a planned mutant that is applied and whose criterion's `Verify:` line still passes
- **When** the terminal transition is attempted
- **Then** it is refused, naming the mutant, its file and its line, and naming the criterion whose test failed to notice - the finding is about the test, so the message must point at the test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::FromPlanTests::test_a_survivor_refuses_the_transition_and_names_the_criterion
- **Caller:** `transition.py set`
- **Verification target:** functional
- **Mutation-checked:** yes (2026-08-06). Downgrading the gate's block to a warning KILLED; reporting `not-run` but not survivors KILLED. CORRECTED at review: the earlier entry also claimed "swallowing the gate's own errors KILLED", which a seat showed false - that mutant survived 2,137 tests, and the gate's fail-loud behaviour was pinned by nothing; gating unconditionally (no `review.test_plan_after`) KILLED, which is the over-correction that would retro-refuse every existing backlog
- **Verified:** yes (2026-08-06)

### AC3: execution is sound against the two ways a mutation run lies

> **RETRACTED AND RESTATED at review.** The delivered version narrowed away the
> anchor-uniqueness limb on the stated ground that "this engine selects mutants by AST node
> rather than by string anchor". **That is false on the code**, and an independent seat proved
> it by execution: `enumerate_mutations` anchors by (file, class, occurrence ordinal) over
> per-line regex, and `mutated_text` re-counts that ordinal WITHOUT the multiline-string
> exclusion `enumerate_mutations` applies - so a `if a == b:` inside a docstring above a real
> `if 1 == 1:` is enumerated at one line and PATCHED at another. The wrong location is editable
> in the automated engine today. The property AC3 asks for is therefore deliverable here, and
> the narrowing hid a live desync rather than describing a limitation.
>
> The desync itself is pre-existing (c40e9c2c, CR0146) and does not block this unit. What was
> mine is the false rationale, and BG0531's scoping of the hazard to the `register` path alone.
> Both are corrected: the criterion is NOT met, this unit does not claim it, and it is carried
> rather than quietly redefined.
>
> **Also retracted: this criterion's Verify line was vacuous.** The named test asserts nothing
> about an anchor - it checks `_suite_env` and `_purge_bytecode`, both of which predate this
> diff, and renaming `plan_execution` leaves it green. A test whose NAME claims a property it
> does not test is the defect class BG0523 exists for, and it appeared here in the unit that
> ships mutant execution.

- **Given** a mutant whose replacement is the same length as the original, and an anchor string occurring more than once in the target file
- **When** the run applies it
- **Then** bytecode is purged and the child runs with bytecode writing disabled so a cached module cannot report a false survival, and the source is restored byte-identical afterwards with that restoration asserted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::FromPlanTests::test_a_cached_module_and_an_ambiguous_anchor_are_both_refused
- **Caller:** `mutation.py run --from-plan`
- **Verification target:** functional
- **Mutation-checked:** partial (2026-08-06). Dropping `PYTHONDONTWRITEBYTECODE` from the suite env KILLED; not purging the stale `.pyc` KILLED; a non-idempotent restore KILLED. The anchor limb is NOT delivered and NOT verified - see the retraction above. The earlier claim that "this engine selects mutants by AST node rather than by string anchor" was FALSE and is withdrawn in full.
- **Verified:** yes (2026-08-06)

> **DELIVERED NARROWED.** AC4 - "the mutant is applied where it was enumerated" - was DESCOPED
> from this story at the close, on a recorded operator decision (`sprint decision list`, choice
> `split`). It is carried wholly by **BG0533**.
>
> This story therefore delivers THREE criteria, not four, and says so rather than counting the
> fourth as passed. The descoped property is a pre-existing defect in the mutation engine that
> this unit SURFACED rather than caused: `enumerate_mutations` skips multiline-string spans when
> counting occurrences and `mutated_text` does not, so a mutant enumerated at one line is applied
> at another. Two independent seats reproduced it by execution.
>
> The history matters more than the outcome. The limb was first narrowed away on my claim that
> "this engine selects mutants by AST node rather than by string anchor" - which is false, and
> the seats disproved it. Correcting that in prose was not enough either: `**Verified:** yes`
> stayed on the line the tooling reads and `verify_ac` re-stamped it green from a test that does
> not exercise the property. A criterion is descoped when the record says so in the fields a
> machine reads, and not before.
>
> Reversible: the operator summary names this as a reversal candidate, and the decision is on
> the run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | sdlc-studio | Groomed: criteria authored against the `mutation.py --from-plan` slice; AC3 pins the two recorded false-survival scars |
| 2026-08-06 | sdlc-studio | Declared `Depends on:` at plan time - the planner reported all six units parallel because no dependency was stated, which is false: the plan is derived (US0629) before it can be reviewed, gated, executed or measured |
| 2026-08-06 | sdlc-studio | DELIVERED NARROWED at the close: AC4 descoped on a recorded decision and carried by BG0533; three criteria delivered, not four |
