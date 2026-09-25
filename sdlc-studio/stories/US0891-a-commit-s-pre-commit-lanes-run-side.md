# US0891: A commit's pre-commit lanes run side by side

> **Status:** Done
> **Findings-filed-to:** BG0759
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, tools/tests/test_lean_precommit_parallel.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_message_first_gate.py, tools/tests/test_precommit_window_guard.py
> **Epic:** EP0262
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change
**I want** the cheap pre-commit lanes, the gate block included, to run concurrently while their output still reads in a fixed order
**So that** every commit, docs-only ones included, pays for its slowest lane rather than the sum of all of them (67s measured, about 22s expected)

## Acceptance Criteria

- **AC1:** Given the real pre-commit hook in the hermetic hook fixture with five lanes stubbed to sleep 2s each, when a commit runs, then the hook's wall time is under 60% of the lanes' summed 10s - the lanes, the gate block included, run concurrently rather than in sequence
  - **Verify:** pytest tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::test_the_lanes_run_concurrently
  - **Verified:** yes (2026-09-25)
- **AC2:** Given stub lanes that finish in the reverse of their declared order, when the hook prints, then each lane's ok or FAIL block appears whole and in declared order, never interleaved with another lane's output, on each of three runs
  - **Verify:** pytest tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::test_output_prints_in_declared_order_whatever_finishes_first
  - **Verified:** yes (2026-09-25)
- **AC3:** Given one lane that fails, when the commit runs, then it is refused with that lane's enforces, details and fix lines, every other lane's verdict still prints, and the suite handover is skipped and named exactly as before; given every lane passing, the selection is handed to commit-msg unchanged
  - **Verify:** pytest tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::test_a_failing_lane_still_refuses_and_skips_the_suites
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
