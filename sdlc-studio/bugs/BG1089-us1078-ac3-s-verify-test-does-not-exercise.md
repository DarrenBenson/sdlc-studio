# BG1089: US1078 AC3's Verify test does not exercise the verdict's binding to the tree sent; only a sibling test does

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/stories/US1078-run-suite-sh-runs-the-full-suite-on.md, tools/tests/test_run_suite_remote.py, changelog.d/BG1089.md
> **Evidence:** US1078 QA review, round 2 (APPROVE), qa-seat-US1078-r1, 2026-10-19, at 82af17f5: narrative ruling on round-1 finding 2.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T17:33:32Z

## Summary

The binding of a host run's verdict to the tree SENT is pinned by `test_an_edit_made_while_the_host_runs_is_not_covered`, which is on no criterion's Verify line. AC3's own test passes when the verdict is bound to the tree as it stands after the run, so `verify_ac` reports AC3 verified without the mid-run case. The full suite catches it at push.

## Steps to Reproduce

Bind run-suite.sh's `TREE_HASH` to `tree_state` after the run and run AC3's Verify test alone: green.

## Proposed Fix

Add the mid-run test to AC3's Verify line, or fold its assertion into AC3's test.

## Acceptance Criteria

- [ ] **AC1** Given the verdict bound to the tree after the run, when US1078's AC3 Verify runs, then it fails
  - **Verify:** pytest tools/tests/test_run_suite_remote_binding.py::RunSuiteBindingTests::test_ac3_sees_the_binding

## Impact

A Verify-only check of US1078 does not cover the claim the unit adds.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): Won't Fix, not beneficial (LL0056): its mutant is already killed by a sibling test in the same module |
