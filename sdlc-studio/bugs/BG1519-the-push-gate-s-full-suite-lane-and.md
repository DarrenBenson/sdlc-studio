# BG1519: The push gate's full-suite lane and gate.py --run-tests pass a run in which no test ran

> **Status:** Fixed
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .githooks/commit-msg, sdlc-studio/tsd.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_commit_msg_hook.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, tsd lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/scripts/gate.py `_full_suite` line 906 (`if cp.returncode not in (0, 5):     # 5: a phase that collected nothing`); `--run-tests` line 2810 (`if code not in (0, 5)`); .githooks/commit-msg lines 443-468 (`suite-collapse`, guarded by `if [ "$ran_pytest" -eq 0 ]`)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:21:48Z

## Summary

In `gate.py`, both `_full_suite` and the `--run-tests` loop accept pytest exit code 5, nothing collected, as a pass for every phase including the main one. The lane the project calls the full-suite check therefore prints PASS over a suite that ran nothing, or one in which every test was skipped. The only defence against a collapsed suite, the `suite-collapse` lane in `.githooks/commit-msg`, runs solely on the unittest fallback path, and pytest is a declared prerequisite, so on a prepared clone, the gate host and CI no boundary compares a test count with anything. The `--list` output of commit-msg still advertises `suite-collapse`, `skill-tests` and `tool-tests` without saying they do not run when pytest is installed. This contradicts the TSD's own rule that a lane with nothing to prove must not read as proof, and it disagrees with `verify_ac`, which reads no-tests and all-skipped as red.

## Steps to Reproduce

1. Create a scratch directory holding an sdlc-studio folder and one file tools/tests/`test_empty.py` that defines no tests.
2. Run gate.py there with --root set to the fixture, --boundary push and --only full-suite: it prints a PASS line for full-suite reading no tests ran, then gate: PASS, and exits 0.
3. Add a second module whose only test class is skipped and repeat: the lane passes with 1 skipped and exits 0.
4. Run gate.py with --run-tests over the same module: it prints no tests ran and exits 0.
5. Read .githooks/commit-msg lines 443 to 468: the collapse check sits inside the branch taken only when pytest did not run.

## Proposed Fix

Count the tests that ran across all phases in `_full_suite` and in the `--run-tests` loop, and refuse when the total is zero or when every test was skipped; keep exit 5 acceptable only for a secondary phase while another phase ran at least one test. Either run the collapse check on the pytest path as well, by reading the count from pytest's summary line, or make the commit-msg lane list say which lanes run only without pytest. State the count floor in the TSD. Pin the empty-suite and all-skipped refusals, each with a passing control, in the gate tests.

## Acceptance Criteria

- [ ] **AC1** Given a fixture root whose only test module defines no test, when `gate.py --root <fixture> --boundary push --only full-suite` runs, then the full-suite lane fails saying no test ran and the gate exits non-zero; the same fixture with one passing test passes. Fails on: a PASS line printed over a suite that collected nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::FullSuiteCountFloorTests::test_an_empty_suite_fails_the_full_suite_lane
  - **Verified:** yes (2026-11-18)
- [ ] **AC2** Given a fixture whose every test is skipped, when the same lane runs, then it fails saying every test was skipped; a fixture with one passing and one skipped test passes, and a secondary phase that collects nothing still passes while another phase ran at least one test. Fails on: an all-skipped suite reading as green, or exit 5 from a secondary phase refusing a suite that did run tests.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::FullSuiteCountFloorTests::test_an_all_skipped_suite_fails_and_an_empty_secondary_phase_does_not
  - **Verified:** yes (2026-11-18)
- [ ] **AC3** Given a test module that defines no test, and one whose only tests are skipped, when `gate.py --run-tests` runs over each, then it exits non-zero naming the zero count; a module with one passing test exits 0. Fails on: `--run-tests` printing no tests ran and exiting 0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::FullSuiteCountFloorTests::test_run_tests_refuses_a_run_in_which_no_test_ran
  - **Verified:** yes (2026-11-18)
- [ ] **AC4** Given a clone with pytest installed, when `.githooks/commit-msg --list` is read against what the hook runs, then every lane it prints either runs on the pytest path or is marked as running only without pytest (`suite-collapse`, `skill-tests` and `tool-tests` today), and `sdlc-studio/tsd.md` states the count floor the gate now holds. Fails on: a lane listed without qualification that does not run on a prepared clone, or a TSD silent on the floor.
  - **Verify:** pytest tools/tests/test_commit_msg_hook.py::ACollapsedSuiteLeavesNoReusableGreenTests::test_the_lane_list_marks_lanes_that_run_only_without_pytest
  - **Verified:** yes (2026-11-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
