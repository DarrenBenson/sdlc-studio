# US0629: a test plan is DERIVED from the unit's criteria by the tooling, naming per criterion the production change the test must fail on

> **Status:** Ready
> **Delivers:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/templates/core/test-spec.md
> **Epic:** EP0207
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer about to write a unit's tests
**I want** the test plan derived from the unit's own acceptance criteria by the tooling, one row per criterion, each naming the production change its test must fail on
**So that** a criterion cannot be silently missing from the plan, which is how four mechanisms shipped in one sprint with passing suites that survived their own deletion

## Acceptance Criteria

### AC1: the plan has exactly one row per criterion, and the count is enforced rather than intended

- **Given** a unit carrying N acceptance criteria
- **When** `verify_ac.py testplan derive --unit <id>` runs
- **Then** it emits exactly N rows keyed by criterion id, and refuses to write a plan whose row count differs from the criteria it read, because a plan assembled by hand is exactly where a criterion goes missing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanDeriveTests::test_every_criterion_gets_exactly_one_row
- **Caller:** `verify_ac.py testplan derive` (the CLI verb), reached by `transition.py set --status "In Progress"` via US0630
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - dropping the row-count equality must turn this test red
- **Verified:** no

### AC2: each row names a concrete production edit, and a row that merely restates its criterion is refused

- **Given** a derived plan whose mutant field for a criterion is blank, or is that criterion's own text with the polarity flipped
- **When** the plan is written
- **Then** `derive` refuses that row, naming the criterion and demanding a named file plus the edit to make in it, because a mutant is a change to production code and "the feature does not work" is not one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanDeriveTests::test_a_restated_criterion_is_not_a_mutant
- **Caller:** `verify_ac.py testplan derive`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - accepting a blank mutant field must turn this test red
- **Verified:** no

### AC3: the plan lives in the unit's own file, so it travels with the unit and files stay truth

- **Given** a unit with no `## Test Plan` section
- **When** `derive` runs, and then runs a second time over its own result
- **Then** the section is written into the unit's own markdown, the second run is a no-op that says so, and an existing hand-authored mutant is preserved rather than overwritten, because naming the mutant is the judgement and only the row set is derived
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanDeriveTests::test_derive_is_idempotent_and_preserves_authored_mutants
- **Caller:** `verify_ac.py testplan derive`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - overwriting an authored mutant must turn this test red
- **Verified:** no

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | sdlc-studio | Groomed: criteria authored against the `verify_ac.py testplan` slice |
