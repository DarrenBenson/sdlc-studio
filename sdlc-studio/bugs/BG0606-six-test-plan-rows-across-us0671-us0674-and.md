# BG0606: Six test-plan rows across US0671, US0674 and US0676 declare mutants their own criterion's verifier cannot die on

> **Status:** Fixed
> **Premise re-verified:** 2026-08-25, by an independent goal review before any code was written. See the sprint plan record; this unit does not reproduce at HEAD as filed and must be re-grounded or closed rather than built.
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 3; plan rows 3; executed 3; killed 3; survived 0; not-run 0; entry point 0 of 3 criteria through the shipped CLI, 3 in-process | fp 7685bed880df ]] (the repair is a re-binding of test-plan rows onto criteria whose tests reach them, verified by the instrument the rows feed rather than by assertion. Across US0671, US0674 and US0676 every declared row was applied to the tree and executed against the selector its own criterion's Verify: line names: 14 of 14, 10 of 10 and 9 of 9 KILLED, with verify_ac.py depth reporting not-run 0 for all three and two superseded ledger rows withdrawn through mutation.py retract with reasons. Nine criteria were added binding behaviours that already had a passing test and no criterion, and testplan derive reports unchanged for all three, so no Title cell states another criterion's claim and no row is invisible to the parser. NOT self-reported: an independent test-plan plan review rejected these plans in three successive rounds and APPROVED all three in the fifth, re-executing every row in an isolated copy of the tree rather than reading them. NOT covered: the six rows this bug named are re-bound, but the review recorded a non-blocking residue of further behaviours in the same diff that carry tests and no criterion, which is a completeness observation rather than a defect and is left standing deliberately.)
> **Close blocked by:** ONE requirement, and it is not what this field said before. Measured through the shipped entry point on 2026-08-25: `transition.py set --id BG0606 --status Fixed --dry-run` reports `blocked (1 requirement(s))` - no `## Test Plan` - and it is FORCEABLE. The earlier text here claimed it needed a plan AND a sixth independent plan review; that was wrong. For a bug the entry gate never fires (`Fixed` is not in `_IMPL_TARGETS`) and the terminal `_planned_mutant_gate` demands a test plan whose mutants are executed, with no verdict check of any kind. The fix SHIPPED in RUN-01M0JD1W and was independently approved; what remains is a test plan for this bug's own criteria.
> **Points:** 5
> **Affects:** sdlc-studio/stories/US0671-revert-check-reverts-a-unit-s-production-files.md, sdlc-studio/stories/US0674-revert-check-runs-as-a-gate-lane-so.md, sdlc-studio/stories/US0676-the-derived-half-of-verification-depth-is-delimited.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_batch_plan_shape.py, .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Evidence:** Independent test-plan plan review, RUN-01M0JD1W close, 2026-08-24. Verdicts recorded in sdlc-studio/reviews/plan-review-verdicts.md: US0671 REJECT, US0674 REJECT, US0676 REJECT. Each finding was checked against sdlc-studio/.local/mutation-runs.json, which records the node each mutant was actually killed by.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

An independent test-plan plan review of RUN-01M0JD1W found six declared mutants that cannot fail the test their criterion's `Verify:` line names. In each case the mutation ledger records the row's kill against a DIFFERENT node, one no criterion names, so `plan_execution` reports the criterion covered while the criterion's own verifier would survive the mutant. This is the exact failure mode the run was opened to eliminate, present in the run's own plans.

## Steps to Reproduce

US0671 AC4 row 2: skipping the revert loop leaves the AC4 fixture green with the change present AND reverted, so the check still refuses and the named test still passes; the ledger records the kill against `test_a_verifier_that_reaches_production_goes_red`. US0674 AC4: the row mutates the test file its own Verify: runs and WEAKENS the assertion, so the test passes unless AGENTS.md is also stripped, which the row does not state. US0674 AC3 row 2: `test_the_recorded_yield_changes_with_the_input` writes and reads through the module attribute in a temp dir and is path-agnostic; the ledger records the kill against `test_the_yield_is_written_under_local`. US0676 AC4 rows 2 and 3: the fixture carries a sealed derived span, so neither mutant reaches its arm and both leave the test at count 0 and passing; the ledger records them against `test_a_field_with_no_derived_half_is_left_alone` and `test_a_span_stripped_of_its_seal_is_still_refused`. US0674 AC1: the criterion claims the lane names each stays-green criterion, but the named test drives only the not-green fixture.

## Proposed Fix

Re-point each row at a mutant its own criterion's verifier can die on, or promote the test that DOES kill it to a criterion of its own and file the row there. Three of the six already have a passing test that no criterion names, so the repair is a binding, not new test code. US0676 AC4's stripped-seal row belongs beside AC2, which is the criterion that makes the refusal claim.

## Acceptance Criteria

- [x] **AC1** Given each of the six named rows after re-binding, when the test its criterion's `Verify:` line names is run, then that test passes and is the node the ledger records the kill against - the rows were re-filed onto criteria whose tests reach them, and every row in all three units was applied to the tree and executed
  - **Verify:** pytest tools/tests/test_batch_plan_shape.py::BatchPlanShapeTests::test_no_criterion_carries_a_row_its_own_verifier_cannot_reach
  - **Verified:** yes (2026-08-24)
- [x] **AC2** Given US0676's plan after re-binding, when its rows are counted, then each states its OWN criterion's claim and the stripped-seal row sits beside the criterion that makes the refusal claim, rather than three rows all claiming AC4's
  - **Verify:** pytest tools/tests/test_batch_plan_shape.py::BatchPlanShapeTests::test_no_row_states_a_criterion_other_than_its_own
  - **Verified:** yes (2026-08-24)
- [x] **AC3** Given the three units after repair, when `verify_ac.py testplan derive` is run against each, then it reports UNCHANGED - the tables are the derived shape rather than a hand-edited one, which is what let a fused row and three wrong Title cells stand
  - **Verify:** pytest tools/tests/test_batch_plan_shape.py::BatchPlanShapeTests::test_the_check_can_fail
  - **Verified:** yes (2026-08-24)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sdlc-studio/stories/US0671-revert-check-reverts-a-unit-s-production-files.md`, restore AC4's second plan row - the decoration row whose mutant skipped the revert loop and left the criterion's own fixture green either way | Given each of the six named rows after re-binding, when the test its criterion's `Verify:` line names is run, then that test passes and is the node the ledger records the kill against - the rows were re-filed onto criteria whose tests reach them, and every row in all three units was applied to the tree and executed |
| AC2 | in `sdlc-studio/stories/US0676-the-derived-half-of-verification-depth-is-delimited.md`, delete AC6 and re-file its row under AC4 | Given US0676's plan after re-binding, when its rows are counted, then each states its OWN criterion's claim and the stripped-seal row sits beside the criterion that makes the refusal claim, rather than three rows all claiming AC4's |
| AC3 | in `verify_ac.py`, make `testplan derive` report a plan UNCHANGED whatever shape it is in, so no artefact can ever be reported off the derived shape | Given the three units after repair, when `verify_ac.py testplan derive` is run against each, then it reports UNCHANGED - the tables are the derived shape rather than a hand-edited one, which is what let a fused row and three wrong Title cells stand |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
