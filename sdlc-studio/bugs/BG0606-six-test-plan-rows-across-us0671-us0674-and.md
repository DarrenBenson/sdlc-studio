# BG0606: Six test-plan rows across US0671, US0674 and US0676 declare mutants their own criterion's verifier cannot die on

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** sdlc-studio/stories/US0671-revert-check-reverts-a-unit-s-production-files.md, sdlc-studio/stories/US0674-revert-check-runs-as-an-advisory-gate-lane.md, sdlc-studio/stories/US0676-the-derived-half-of-verification-depth-is-delimited.md
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

- [ ] **AC1** Given each of the six named rows, when its declared mutant is applied and ONLY the criterion's own `Verify:` selector is run, then that selector goes red
- [ ] **AC2** Given US0676 AC4, when its rows are counted, then the plan declares one row per claim AC4 actually makes and the stripped-seal row sits on the criterion that makes the refusal claim
- [ ] **AC3** Given the three units after repair, when `mutation.plan_execution` is read, then no row's recorded kill node is absent from the criterion's own Verify: line

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
