# BG1088: A setup fault on a gate host's suite run is named as 'did not run the all suite' with no test that fails without it

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_run_suite_setup_fault.py, changelog.d/BG1088.md
> **Evidence:** US1078 QA review, round 2 (APPROVE), qa-seat-US1078-r1, 2026-10-19, at 82af17f5: [new] item 1, tools/remote-gate.sh:157-160.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T17:33:26Z

## Summary

US1078's repair made remote-gate.sh name what did not run on a host setup fault (exit 4): 'the <suite> suite' for a suite run, 'the gate' otherwise. A prereq refusal on a suite run prints 'did not run the all suite', but restoring 'did not run the gate' leaves `test_run_suite_remote.py`, `test_remote_gate_push.py` and `test_remote_gate_runs.py` green. Only the exit code is pinned.

## Steps to Reproduce

Change remote-gate.sh's ran="the $suite suite" back to the gate's wording and run the three modules: green.

## Proposed Fix

Drive a suite run against a fixture host whose prerequisite check refuses, and assert the message names the suite.

## Acceptance Criteria

- [ ] **AC1** Given a suite run whose host refuses at its prerequisite check, when it ends, then the message names the suite that did not run
  - **Verify:** pytest tools/tests/test_run_suite_setup_fault.py::RunSuiteSetupFaultTests::test_a_setup_fault_names_the_suite

## Impact

The wording can regress with the suite green; the exit stays 4 and the run red.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): Won't Fix, not beneficial (LL0056): message wording only; the exit code and the red run are already pinned |
