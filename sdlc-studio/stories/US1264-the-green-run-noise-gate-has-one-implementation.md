# US1264: The green-run noise gate has one implementation that CI and the push both read, and the second copy is retired

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0712
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/run-suite.sh, tools/test_noise.py, tools/tests/test_test_noise.py
> **Epic:** EP0352
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** The green-run noise gate has one implementation that CI and the push both read, and the second copy is retired
**So that** CR0712 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: CI and the push refuse the same noisy green run through one command

- **Given** a fixture suite whose passing test prints a diagnostic line over the budget, and a second fixture inside the budget
- **When** the noise gate is run over each by the command lint.yml names and by the command the push hook names
- **Then** the two commands are the same entry point, it refuses the first fixture naming the test that printed, and it passes the second. Fails on: a green run with leaked diagnostics refused at one boundary and passed at the other
- **Verify:** pytest tools/tests/test_test_noise.py::OneNoiseGateTests::test_ci_and_push_run_the_same_noise_gate_and_agree

### AC2: The detector and the ceiling live in one place

- **Given** `tools/test_noise.py`, `tools/run-suite.sh` and the CI workflow
- **When** the leak detector or a module's ceiling is changed in `tools/test_noise.py` alone
- **Then** both boundaries follow the change, and `tools/run-suite.sh` holds no embedded copy of the capture plugin, the detector or the ceiling arithmetic. Fails on: a second copy that keeps the old rule, as the plugin written inline in `run-suite.sh` does at HEAD
- **Verify:** pytest tools/tests/test_test_noise.py::OneNoiseGateTests::test_run_suite_holds_no_second_copy_of_the_noise_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
