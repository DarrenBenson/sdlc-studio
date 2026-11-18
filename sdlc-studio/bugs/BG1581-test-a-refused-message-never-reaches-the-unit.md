# BG1581: test_a_refused_message_never_reaches_the_unit_suites fails by 4 ms on the gate host under the nested unittest run, refusing a push

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/tests/test_message_first_gate.py, tools/tests/test_lean_ci_unittest_run.py
> **Evidence:** Push gate on devserver1, 2026-11-18, log boundary-suite-last.log lines 302-355.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T03:05:04Z

## Summary

Inside `test_lean_ci_unittest_run`'s nested unittest run, `test_message_first_gate`'s wall-clock check asserted a refused commit cost less than the full run minus half the suite cost: 3.802s against a bound of 3.798s, so the push boundary refused commit 3777e27e. The same test is skipped under pytest as covered by BudgetAcrossThePairTests without the wall-clock cost, and passed locally on re-run.

## Steps to Reproduce

Run tools/tests/`test_lean_ci_unittest_run.py` on the gate host under load.

## Proposed Fix

Judge the skip from the lane log the way BudgetAcrossThePairTests does, not from wall-clock time, or skip it in the nested run as pytest does.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Inside `test_lean_ci_unittest_run`'s nested unittest run, `test_message_first_gate`'s wall-clock check asserted a refused commit cost less than the full run...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run tools/tests/`test_lean_ci_unittest_run.py` on the gate host under load.
- [ ] **AC3** The proposed fix lands, pinned by a test: Judge the skip from the lane log the way BudgetAcrossThePairTests does, not from wall-clock time, or skip it in the nested run as pytest does.

## Impact

A green change is refused at the push by a timing margin.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
