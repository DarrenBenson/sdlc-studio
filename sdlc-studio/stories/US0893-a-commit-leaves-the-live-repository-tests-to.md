# US0893: A commit leaves the live-repository tests to the push

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, pytest.ini, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py
> **Epic:** EP0262
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change to gate.py
**I want** the handful of slow live-repository and boundary tests to run at the push, not in the commit's selection
**So that** a gate.py commit stops paying up to 90s per test for checks the push's full suite already runs

## Acceptance Criteria

- **AC1:** Given a fixture test marked `boundary_only` that writes a marker file when it runs, when `gate.py --run-tests` runs a commit's selection containing it, then the marker is not written, and when the push boundary's full-suite lane runs, it is - the commit excludes the marker and the push includes it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::BoundaryOnlyTests::test_the_commit_skips_boundary_only_and_the_push_runs_it
- **AC2:** Given `test_gate.py`, then the live-repository tests the measurement named (`GateRealWrapperTests::test_real_wrappers_run_and_shape`, `RevertCheckLaneTests::test_the_lane_runs_at_the_boundary_and_not_per_commit`, the `ModuleAloneLaneTests` push-boundary test and the slow `DocSurfaceApplicabilityTests` case) are collected by `pytest -m boundary_only`, and pytest.ini registers the marker beside `serial_only`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::BoundaryOnlyTests::test_the_live_repository_tests_are_boundary_only

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
