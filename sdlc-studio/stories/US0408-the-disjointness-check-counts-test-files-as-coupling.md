# US0408: the disjointness check counts test files as coupling

> **Status:** Draft
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Delivers:** CR0411
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0154
> **Points:** 2

## User Story

**As a** operator deciding whether a batch can be parallelised
**I want** the file-disjointness check that decides parallelisability to count test files as coupling, not only source
**So that** two builders never fan out onto the same test file and collide on merge as this run's builders did

## Acceptance Criteria

### AC1: A shared test file counts as coupling for parallelisability

- **Given** two units that touch different source modules but the same test file
- **When** the delivery mode is determined
- **Then** the shared test file couples the two units and the batch is not offered as parallel, where a source-only check would have called them disjoint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeTestFileCouplingTests::test_a_shared_test_file_counts_as_coupling

### AC2: Test-file coupling collapses the parallel decomposition exactly as module coupling does

- **Given** a batch whose only cross-unit file overlap is a shared test file
- **When** the delivery mode is determined
- **Then** the batch has no parallel form and parallel is withheld, exactly as a shared source module withholds it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeTestFileCouplingTests::test_a_test_file_only_overlap_denies_the_parallel_offer

## Verification depth

Node-addressed pytest ACs over `test_sprint.py`, red before the code (the offer, the test-file coupling and the determinism did not exist). Mutation-proven by hand (`__pycache__` purged, `python3 -B`): loosening the >=2 group threshold, dropping the Verify-derived files from coupling, inverting the record refusal, and removing the no-Affects safety branch were each caught by a node.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built: delivery-mode offer + test-file coupling + determinism, tested, mutation-proven |
