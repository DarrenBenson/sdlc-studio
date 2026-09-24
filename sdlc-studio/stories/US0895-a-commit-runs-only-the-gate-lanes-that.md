# US0895: A commit runs only the gate lanes that can refuse it

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_gate_lanes.py, AGENTS.md
> **Epic:** EP0262
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change
**I want** the eight advisory gate lanes that never block to leave the per-commit gate, with doc-freshness running at the close
**So that** about 70s of every commit stops going on lanes that cannot refuse it, and the one advisory check worth reading arrives once per sprint

## Acceptance Criteria

- **AC1:** Given `gate.py --root .` as the pre-commit hook calls it, when it runs, then doc-freshness, constitution, doc-surface, disclosure, provenance, mutation, hook-enabled and batch-size are never reached (each patched to raise), while conformance, reconcile, validate, integrity and duplicate-id still run and still refuse a planted defect
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_gate_lanes.py::PerCommitLaneTests::test_the_advisory_lanes_leave_the_commit_gate
- **AC2:** Given the gate as `sprint close` calls it (`--require-retro`), then doc-freshness runs there and reports its findings without failing the close; the other seven run only when named with `--only`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_gate_lanes.py::PerCommitLaneTests::test_doc_freshness_runs_at_the_close_and_never_blocks
- **AC3:** Given the test nodes this story deletes (per-commit membership pins such as `test_gate`'s `DEFAULT_CHECKS` set), then every stamped criterion naming one is retired in the D0259 pattern (`Verify: manual - retired by <this story>: <why>`, `Verified: manual (<date>) - retired, superseded by <this story>`), so `verify_ac.py stamps --staged` passes on the deleting commit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_gate_lanes.py::RetiredCriteriaTests::test_criteria_naming_deleted_gate_lane_tests_are_retired

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
