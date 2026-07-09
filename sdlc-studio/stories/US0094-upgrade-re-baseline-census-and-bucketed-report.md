# US0094: Upgrade re-baseline census and bucketed report

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0020
> **Persona:** Engineering seat
> **Affects:** scripts/project_upgrade.py, scripts/tests/test_project_upgrade.py

## User Story

**As an** operator who has just upgraded a project's schema
**I want** a per-artifact census of every non-terminal artifact against the capability delta, bucketed into backfill / re-review / residual
**So that** I get a bounded, prioritised list of what the upgrade left stale instead of discovering each gap as a surprise gate failure

Delivers the read-only reporting core of CR0197. Era-gated: the buckets only populate for capabilities the project has adopted (schema/`adopt_after` watermark).

## Acceptance Criteria

### AC1: The census walks every non-terminal artifact and buckets each gap

- **Given** a project with a mix of terminal and non-terminal artifacts and a known capability delta
- **When** `project_upgrade.rebaseline(root)` runs (read-only)
- **Then** it returns, per non-terminal artifact, its per-capability gaps assigned deterministically (status x delta) to one of `backfill` / `re-review` / `residual`; terminal artifacts are absent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::RebaselineCensusTests
- **Verified:** yes (2026-07-09)

### AC2: The dry-run report lists artifacts by bucket, empty buckets explicit

- **Given** the census result
- **When** `project upgrade` runs its re-baseline report (dry-run)
- **Then** it prints each non-terminal artifact under its bucket with the specific gap named; an empty bucket prints an explicit "none" line rather than being silently omitted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::RebaselineReportTests
- **Verified:** yes (2026-07-09)

### AC3: The era-gate boundary is respected

- **Given** a Done story and a Ready story that both would match a newly-landed gate's trigger
- **When** the census runs
- **Then** the Done (terminal) story is untouched and the Ready story is flagged in the re-review bucket; a capability the project has not adopted produces no gap
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::RebaselineEraBoundaryTests
- **Verified:** yes (2026-07-09)

### AC4: Bucket assignment is deterministic

- **Given** the same project state
- **When** the census runs twice
- **Then** the bucket assignment is identical (no model judgement in the fire/skip decision - TRD ADR-006)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::RebaselineDeterminismTests
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0197 (census + bucketed report) |
