# US0284: test_gate's two real-wrapper tests share one gate execution instead of running it twice

> **Status:** Draft
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0093
> **Points:** 3
> **Persona:** repo maintainer (dogfooding operator)

## User Story

**As a** repo maintainer running the gate on every commit
**I want** the suite to learn what it needs from one real gate execution rather than two
**So that** the 71 seconds two tests currently spend re-deriving the same result is spent once

## Context

Measured 2026-07-21: `test_gate.py` is 72.2s of a 153.1s suite, and 71.1s of that is two
tests. `test_real_wrappers_run_and_shape` (35.56s) calls `run_gate` and asserts the result's
shape. `test_main_returns_exit_code` (35.54s) calls `main` and asserts only that the return
is 0 or 1. The other 199 tests in the file cost 0.8s combined.

The second test is the clearer waste: it pays 35 seconds to learn something a stubbed
`run_gate` proves in milliseconds, because what it actually pins is `main`'s own mapping from
result to exit code, not whether the lanes work. One true end-to-end execution is kept, since
that is the pin that the 15 real lanes wire up and return the documented shape.

## Acceptance Criteria

### AC1: the real gate is executed once for the class, not once per test

- **Given** the real-wrapper tests, which today each drive a full gate run over this repo
- **When** the class runs
- **Then** the real gate is executed exactly once and the shape assertions read that one result
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateRealWrapperTests::test_the_real_gate_runs_once_per_class

### AC2: main's exit-code contract is pinned without re-running the gate

- **Given** a stubbed `run_gate` returning a known result
- **When** `main` is called
- **Then** the exit code it derives is asserted against that result, so the test pins main's own
  mapping rather than re-discovering it from a live run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateRealWrapperTests::test_main_maps_result_to_exit_code_without_rerunning

### AC3: exactly one true end-to-end execution survives

- **Given** the whole test file after the change
- **When** its real-gate call sites are counted
- **Then** exactly one unstubbed end-to-end execution remains, so the real lanes are still wired
  up by a test rather than only by assertion of a cached shape
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateRealWrapperTests::test_exactly_one_unstubbed_end_to_end_run

### AC4: no assertion is lost

- **Given** the assertions the two tests made before the change - `ok` is a bool, there are 15
  checks, each carries the same 5 keys, and the exit code is 0 or 1
- **When** the file runs after the change
- **Then** every one of those assertions is still made
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py

### AC5: the saving is measured, not assumed

- **Given** the 72.2s baseline measured on 2026-07-21
- **When** the change is delivered
- **Then** the measured wall time is recorded against that baseline
- **Verify:** manual record the measured time at delivery. Deliberately not executable: a
  standing wall-clock threshold is machine-dependent and would un-Done this story on an
  unrelated slower run (the lesson from BG0234).
- **Verified:** manual

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Created via `new` (deterministic) |
