# BG1581: test_a_refused_message_never_reaches_the_unit_suites fails by 4 ms on the gate host under the nested unittest run, refusing a push

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_message_first_gate.py, changelog.d/BG1581.md
> **Evidence:** Push gate on devserver1, 2026-11-18, log boundary-suite-last.log lines 302-355.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T03:05:04Z

## Summary

Inside `test_lean_ci_unittest_run`'s nested unittest run, `test_message_first_gate`'s wall-clock check asserted a refused commit cost less than the full run minus half the suite cost: 3.802s against a bound of 3.798s, so the push boundary refused commit 3777e27e. It passed locally on re-run. The same assertion runs under pytest too (`MessageBeforeSuitesTests`, not one of the `TotalSpansBothHooksTests` methods that skip as covered by BudgetAcrossThePairTests), and the lane log it already reads (`_ran()`) proves the skip without the clock.

## Steps to Reproduce

1. Read `tools/tests/test_message_first_gate.py::MessageBeforeSuitesTests::test_a_refused_message_never_reaches_the_unit_suites`
   at HEAD: after asserting the lane log is empty, it asserts
   `refused_secs < ok_secs - SUITE_COST_SECONDS / 2`, a 0.5 s margin over wall-clock.
2. Run it with the refused commit's measured time raised by a 1.2 s scheduling spike (a subclass
   whose `_commit` adds 1.2 s to the refused commit and changes nothing the hooks run).

Measured at HEAD 3791e5193: the spiked run fails with `2.61 not less than 2.46 : the refusal cost
2.61s against 2.96s for the full run - it did not skip the expensive lanes`, while the lane log
for that refused commit is empty (`ran=[]`). Six unspiked runs under 24 busy loops on 8 cores
passed, so the flake needs the gate host's load to show; the spike shows the assertion judges the
clock, not the lanes.

## Proposed Fix

Drop the wall-clock assertion and judge the skip from the lane log alone, as
BudgetAcrossThePairTests does; with no clock claim left, set the class's `SUITE_COST_SECONDS` to 0
so the module stops paying a second per commit for it. Add a spiked subclass that inherits the
refusal test, so a wall-clock assertion brought back fails. No change to
`test_lean_ci_unittest_run.py` is needed: it runs the module as CI does and goes green with it.

## Acceptance Criteria

- [ ] **AC1** Given the refused commit's measured time is raised by a 1.2 s scheduling spike and the hooks run unchanged, when the refusal test runs, then it passes, judging the skip from the lane log. Fails on: HEAD's `assertLess(refused_secs, ok_secs - SUITE_COST_SECONDS / 2)` (measured: `2.61 not less than 2.46` with `ran=[]`).
  - **Verify:** pytest tools/tests/test_message_first_gate.py::SpikedRefusalTests::test_a_refused_message_never_reaches_the_unit_suites
  - **Verified:** yes (2026-11-23)
- [ ] **AC2** Given the unspiked fixture, when a subject naming two ids with no `Refs:` refuses, then the lane log records no suite lane, and the same staged change with both trailers commits and records `skill-tests` and `tool-tests`. Fails on: a fix that drops the lane-log assertions or the accepted control along with the clock.
  - **Verify:** pytest tools/tests/test_message_first_gate.py::MessageBeforeSuitesTests::test_a_refused_message_never_reaches_the_unit_suites
  - **Verified:** yes (2026-11-23)
- [ ] **AC3** Given CI's nested `python3 -m unittest` order, when `test_lean_refusal_log` and `test_message_first_gate` run in one process, then every test passes. Fails on: the clock assertion, which refused commit 3777e27e at the push by 4 ms.
  - **Verify:** pytest tools/tests/test_lean_ci_unittest_run.py::CiUnittestRunTests::test_the_gate_fixture_survives_an_importers_teardown
  - **Verified:** yes (2026-11-23)

## Impact

A green change is refused at the push by a timing margin.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-23 | Sam Eriksson (qa) | Groomed for run twenty-four: the wall-clock assertion is still at HEAD and fails on a 1.2 s spike with an empty lane log (measured); Summary corrected (the assertion is not skipped under pytest); three executable criteria; Affects drops `test_lean_ci_unittest_run.py`, which needs no change; 2 to 1 point |
