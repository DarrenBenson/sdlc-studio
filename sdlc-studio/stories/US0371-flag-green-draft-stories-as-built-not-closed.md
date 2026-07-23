# US0371: flag green Draft stories as built-not-closed, forecast the unverified as new, point an all-built batch at the close path

> **Status:** Done
> **Delivers:** CR0366
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0130
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_built_not_closed.py

## User Story

**As a** operator planning a sprint in a repo where work landed outside a run
**I want** sprint plan to notice a Draft story whose executable ACs are already green
**So that** the forecast is not inflated by pricing already-built work as new, and an all-built batch is pointed at the close path

## Acceptance Criteria

### AC1: a green Draft story is flagged built-not-closed, not forecast as new

- **Given** a Draft story whose executable ACs all pass
- **When** sprint plan selects a batch containing it
- **Then** the plan flags it as built-not-closed and excludes it from the build forecast rather than pricing it as new work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_built_not_closed.py::BuiltNotClosed::test_green_draft_flagged_not_forecast_as_new
- **Verified:** yes (2026-07-23)

### AC2: the flag does not fire on unverified stories

- **Given** a Draft story with failing or unrun ACs
- **When** sprint plan runs
- **Then** it is forecast as ordinary unbuilt work and is not flagged built-not-closed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_built_not_closed.py::BuiltNotClosed::test_unverified_draft_forecast_as_new
- **Verified:** yes (2026-07-23)

### AC3: an all-built batch is pointed at the close path

- **Given** a batch in which every unit is built-not-closed
- **When** sprint plan runs
- **Then** it says so plainly and points at the close path instead of a build
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_built_not_closed.py::BuiltNotClosed::test_all_built_batch_points_at_close
- **Verified:** yes (2026-07-23)

## Verification depth

All three ACs are node-addressed pytest verifiers over `test_built_not_closed.py` and were red
before the code (the predicate, the exclusion and the all-built flag did not exist). Mutation-proven
by hand (`__pycache__` purged, `python3 -B`): dropping the failed/stale guard, loosening the
all-built flag to fire on a mixed batch, and removing the `continue` that skips pricing were each
caught by a node.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built: predicate + forecast exclusion + all-built close-pointer, tested, mutation-proven |
