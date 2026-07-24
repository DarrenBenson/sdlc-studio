# US0379: mutation.py records an empty surface as a first-class outcome and the gate lane reads it distinct from not-run and PASSes

> **Status:** Review
> **Delivers:** CR0376
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0137
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py

## User Story

**As an** operator closing a docs-only change through the mutation gate
**I want** an empty surface recorded as a first-class outcome, not a silent pass
**So that** 'nothing to mutate' reads distinct from not-run and from a clean sweep

## Acceptance Criteria

### AC1: mutation.py run over a surface with no mutatable files can emit a report recording the empty

- **Given** a mutation run over a surface with no mutatable sites (a docstring/import-only module)
- **When** the run executes
- **Then** mutation.py run over a surface with no mutatable files can emit a report recording the empty surface as the honest outcome (exit 0 under an explicit flag or a distinct recorded status), never a silent pass
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::EmptySurfaceIsFirstClassTests::test_run_over_a_no_site_surface_records_the_empty_surface
- **Verified:** yes (2026-07-24)

### AC2: the gate's mutation lane reads that report as 'nothing to mutate' - distinct from not-run and from

- **Given** a mutation report recording an empty surface
- **When** the gate's mutation lane reads it
- **Then** the gate's mutation lane reads that report as 'nothing to mutate' - distinct from not-run and from PASS - so a docs-only close is green with the reason on the record
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::EmptySurfaceIsFirstClassTests::test_the_gate_lane_reads_empty_surface_distinct_from_not_run_and_pass
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
