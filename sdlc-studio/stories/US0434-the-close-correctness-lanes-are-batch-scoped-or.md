# US0434: the close correctness lanes are batch-scoped, or --file-and-close files named out-of-batch debt

> **Status:** Done
> **Delivers:** CR0421
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0162
> **Points:** 3

## User Story

**As an** operator closing a fully delivered batch in a clean tree
**I want** the close's correctness lane to judge this batch's units, not the whole workspace
**So that** out-of-batch debt authored by someone else - a different epic, missing `verified` because
its ACs are manual - does not block an in-batch close, without forcing me to grandfather it past a cutoff

## Acceptance Criteria

### AC1: the close correctness lane is scoped to the batch

- **Given** a clean tree holding several nonconformant Done units, of which only one is in the batch
- **When** the conformance lane is judged with the batch as its scope
- **Then** it charges only the in-batch unit - the out-of-batch units are reported but not counted,
  so the whole-workspace scan no longer binds an in-batch close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::BatchScopedConformanceTests::test_close_conformance_lane_judges_only_the_batch
- **Verified:** yes (2026-07-26)

### AC2: the batch scope threads through the close's gate run

- **Given** a clean tree with out-of-batch conformance debt
- **When** `run_gate` is invoked with the run's batch as `conformance_scope`, exactly as the sprint
  close invokes it
- **Then** the close run's conformance check drops the out-of-batch units from its count, so the
  scope reaches the lane end to end rather than only at the unit function
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::BatchScopedConformanceTests::test_run_gate_scopes_conformance_to_the_batch
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
