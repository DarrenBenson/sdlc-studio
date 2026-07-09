# US0095: Upgrade re-baseline mechanical backfill and next-transition policy

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0020
> **Persona:** Engineering seat
> **Affects:** scripts/project_upgrade.py, reference-upgrade.md, scripts/tests/test_project_upgrade.py
> **Depends on:** US0094

## User Story

**As an** operator re-baselining after an upgrade
**I want** `--apply` to perform only the deterministic backfill (never the re-review), idempotently and without inventing history
**So that** the mechanical gaps close in one safe pass while judgement gaps stay in my hands

Delivers CR0197's `--apply` half + the never-retroactive policy. Depends on US0094's census.

## Acceptance Criteria

### AC1: --apply performs only the mechanical backfill bucket

- **Given** a census with entries in all three buckets
- **When** `project upgrade --apply` runs
- **Then** it applies only the `backfill` bucket (deterministic, read-only-to-compute stamps: `route estimate` difficulty on units lacking it, missing schema fields with safe defaults); the `re-review` and `residual` buckets are reported, never auto-actioned
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::BackfillApplyTests

### AC2: --apply is idempotent

- **Given** a re-baseline `--apply` has already run
- **When** it runs a second time
- **Then** it reports nothing to do and changes no files
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::BackfillIdempotencyTests

### AC3: No fabricated history

- **Given** artifacts whose telemetry/metrics fields were absent before the upgrade
- **When** `--apply` runs
- **Then** those past events stay absent (no back-dated rows are invented); recording begins forward only
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::NoFabricatedHistoryTests

### AC4: New gates attach at the next transition, never retroactively

- **Given** a newly-landed gate and an in-flight artifact past the point the gate would have fired
- **When** the re-baseline runs
- **Then** the completed transitions are not retroactively invalidated; enforcement attaches at the artifact's next transition, and that policy is stated in `reference-upgrade.md`
- **Verify:** grep "next transition" .claude/skills/sdlc-studio/reference-upgrade.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0197 (backfill + next-transition policy) |
