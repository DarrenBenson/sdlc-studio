# US0488: sprint next materialises the head charter against the backlog as it is at that moment, and stops when its scope resolves to nothing

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0176
> **Points:** 5

## User Story

**As a** operator returning to a queue somebody planned days ago
**I want** the next charter planned against the backlog as it is at that moment, not as it was when written
**So that** the bugs and lessons the intervening work generated are in the batch, which is why a frozen queue was refused

## Acceptance Criteria

### AC1: the head charter is materialised against the current backlog

- **Given** a queue whose head charter names a scope rule, and a backlog that has changed since it was written
- **When** sprint next runs
- **Then** the batch is resolved from the backlog as it is now, so units created since the charter was authored are included and units since delivered are not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintNextTests::test_the_head_charter_materialises_against_the_current_backlog

### AC2: an empty scope stops and reports, leaving the queue intact

- **Given** a head charter whose scope rule resolves to no units
- **When** sprint next runs
- **Then** it stops, reports that the charter's scope is empty and names it, and the queue is left unchanged rather than the charter being silently skipped or dropped
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintNextTests::test_an_empty_scope_stops_and_reports_without_touching_the_queue

### AC3: materialising respects the one open run slot

- **Given** a run already open
- **When** sprint next runs
- **Then** it refuses rather than merging the charter's batch into the run already open, preserving the single-run-slot rule
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintNextTests::test_next_refuses_while_a_run_is_open

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
