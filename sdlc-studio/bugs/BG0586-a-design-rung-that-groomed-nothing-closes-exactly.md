# BG0586: a design rung that groomed nothing closes exactly like one that groomed everything

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 2; plan rows 2; executed 2; killed 2; survived 0; not-run 0; entry point 0 of 2 criteria through the shipped CLI, 2 in-process | fp ae72f7a3576b ]] (two criteria over the close pre-flight, driven against a REAL git history rather than a stub - the check is silent when git cannot answer, so a fixture that could not answer would exercise the fail-open path and prove nothing. Both mutants executed and killed. NOT covered: whether `pre_work` is recorded anywhere by the batch commands today; this unit reads the field and does not create it)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_rung_product_blockers` asks whether each batch unit IS groomed, not whether THIS RUN groomed it. A design run whose units were all groomed weeks earlier therefore passes with zero blockers and closes clean, having produced nothing. The bar is real - an ungroomed unit blocks - but it is a state check standing in for a work check, and the run's own `base_ref` plus `_delivery_evidence`, the helper defined immediately above it, are exactly what would answer the work question. `render_grooming_report` was written to shout about this precise abuse ('a rung that groomed nothing closes exactly like one that groomed everything') and is print-only, so it warns and never refuses.

## Steps to Reproduce

Found by adversarial review of BG0582's repair, 2026-08-16, and confirmed by execution against a temp repo: a design rung whose single batch unit was groomed BEFORE the run window and which carries zero commits in that window returns 0 blockers from the close pre-flight and reports ready. Compare the same fixture at the `done` rung, which returns a blocking sign-off row. The comparison that matters: base ref = 1 blocking row, patched = 0 blocking rows plus 1 non-blocking one.

## Proposed Fix

Judge the rung against the work, not the state. Candidate shape: a design-rung unit satisfies the bar when it is groomed AND either carries run-window evidence (`_delivery_evidence`, already written and already used by the `done` path) or is explicitly recorded as pre-work. The pre-work exemption is required, not optional - RUN-01M05A5M itself transitioned six units as pre-work by an operator ruling, and a bar without that exemption would refuse a legitimate close. That nuance is why this is filed rather than folded into BG0582: it needs its own criteria and its own review, not a second edit to a gate the author's own run was waiting on.

## Acceptance Criteria

- [ ] **AC1** Given a `design` rung whose units were all groomed before the run and which has no commit naming any of them, when the pre-flight runs, then it reports a blocking row - every per-unit check asks whether the product EXISTS, so a rung that produced nothing closed identically to one that groomed everything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RungTerminalAndProductTests::test_a_rung_that_produced_nothing_in_the_run_is_reported
- [ ] **AC2** Given a unit declared as PRE-WORK when the batch was formed, when the pre-flight runs, then it does not accuse the rung - a legitimate close may carry work groomed earlier; what it may not do is let that be invisible
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RungTerminalAndProductTests::test_a_unit_declared_as_pre_work_does_not_accuse_the_rung

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, delete the batch-level production check from `_rung_product_blockers` | Given a `design` rung whose units were all groomed before the run and which has no commit naming any of them, when the pre-flight runs, then it reports a blocking row - every per-unit check asks whether the product EXISTS, so a rung that produced nothing closed identically to one that groomed everything |
| AC2 | in `sprint.py`, drop the pre-work exclusion from `_rung_product_blockers` | Given a unit declared as PRE-WORK when the batch was formed, when the pre-flight runs, then it does not accuse the rung - a legitimate close may carry work groomed earlier; what it may not do is let that be invisible |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
