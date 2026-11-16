# BG1493: The pre-push boundary gate does not run CI's green-run noise gate, so a push that passes locally turns GitHub Lint red

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** tools/run-suite.sh, tools/remote-gate.sh, .githooks/pre-push, tools/tests/test_run_suite.py, changelog.d/BG1493.md
> **Evidence:** GitHub Actions Lint on 7c64bf26, 2026-11-16 00:00 UTC; BG1489.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T01:57:44Z

## Summary

Run thirteen's US1061/US1062 added a warning that passing tests leaked. The pre-push boundary gate on the gate host passed 7c64bf26, but GitHub's Lint workflow failed on it: tools/skill-tests.sh's green-run noise gate counted 112 diagnostic lines against `_total` 104 (BG1489). The push gate is documented as the full-suite check, yet one CI lane it does not run judged main red after the push. D0181 reads a red main before the next push, and that costs a fix cycle every time.

## Steps to Reproduce

1. Add a test that prints a warning while passing.
2. Push: the pre-push gate passes.
3. GitHub Lint fails on test-noise.

## Proposed Fix

Have the boundary push suite run the skill suite through tools/skill-tests.sh's noise gate (or apply tools/`test_noise.py` to the suite output it already captures) so a leak above the budget refuses the push.

## Acceptance Criteria

- [ ] **AC1** Given a fixture tree whose passing skill test prints more diagnostic lines than its module's budget in tools/test-noise-baseline.json, when the push boundary gate the pre-push hook runs judges it on this machine (`SDLC_GATE_LOCAL=1`), then the push is refused, naming the noise gate and the module over its budget. Fails on: the gate passing it, as it passed 7c64bf26 while GitHub Lint counted 112 diagnostic lines against a budget of 104 (BG1489).
  - **Verify:** pytest tools/tests/test_run_suite.py::PushNoiseGateTests::test_a_passing_test_leaking_above_budget_refuses_a_local_push
- [ ] **AC2** Given the same fixture, when the push is judged on the gate host that `sdlc.gateHost` names (`tools/remote-gate.sh push`), then the host applies the same noise gate and refuses it the same way. Fails on: a host run that passes what a local run refuses.
  - **Verify:** pytest tools/tests/test_run_suite.py::PushNoiseGateTests::test_the_gate_host_applies_the_same_noise_gate
- [ ] **AC3** Given the fixture within its budget, then the push gate passes it on both routes. Fails on: a refusal of a tree within its budget, or a check that reads the test runner's own output as noise and refuses every push.
  - **Verify:** pytest tools/tests/test_run_suite.py::PushNoiseGateTests::test_a_suite_within_budget_passes_the_push

## Notes

- Groomed for EP0314 (run fifteen, wave one). The push boundary is `gate.py --boundary push`, whose `full-suite` lane runs the suite under pytest, which captures a passing test's output, so the leak CI's unittest run prints never reaches it. A gate host run goes through `tools/remote-gate.sh push` and never runs `.githooks/pre-push`'s local branch, so the fix has to reach both routes: `tools/remote-gate.sh` joins Affects and Points rise from 3 to 5. `gate.py` is shipped and `tools/test_noise.py` is repo-only, so keep the noise check in the repo's tooling.
- Fixed before US1173 (the 6.4.0 cut): it is the one open High, so `python3 tools/known_issues.py bar` refuses the cut until it is Fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
| 2026-11-16 | Claude Opus 5.5 (grooming) | Groomed for EP0314: stub criteria rewritten with Verify lines; tools/remote-gate.sh joins Affects for the gate host route; Points 3 to 5 (see Notes) |
