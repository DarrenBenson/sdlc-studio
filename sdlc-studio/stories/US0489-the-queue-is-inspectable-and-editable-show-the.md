# US0489: The queue is inspectable and editable: show the next charter with its goal and resolved contents, insert, cancel, clear and reorder

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0176
> **Points:** 5

## User Story

**As a** operator who planned five sprints and now needs to change one
**I want** the queue to be inspectable and editable - show the next, insert, cancel, clear and reorder
**So that** a plan somebody wrote can be corrected without hand-editing state or throwing the whole queue away

## Acceptance Criteria

### AC1: showing the next charter reports its goal and the contents it would resolve to

- **Given** a queue with charters
- **When** the next charter is shown
- **Then** its goal, scope rule and appetite are reported together with the units it would resolve to against the current backlog, so what will run is visible before it runs
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::QueueCrudTests::test_showing_the_next_charter_reports_its_goal_and_resolved_contents

### AC2: insert, cancel and clear each change the queue and are each recorded

- **Given** a queue of several charters
- **When** a charter is inserted at a position, another cancelled, and the queue cleared
- **Then** each operation changes the order or membership as asked and records what it did, so the queue's history explains its current shape
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::QueueCrudTests::test_insert_cancel_and_clear_change_the_queue_and_are_recorded

### AC3: WSJF order is recomputed at each next, not frozen when the queue was authored

- **Given** a queue ordered by WSJF and a backlog whose values have since changed
- **When** the next charter is resolved
- **Then** the order reflects the recomputed values rather than the ranking recorded at authoring time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::QueueCrudTests::test_wsjf_order_is_recomputed_at_each_next

### AC4: an operation naming a charter the queue does not hold is refused

- **Given** a queue
- **When** cancel or reorder names an id absent from it
- **Then** the operation is refused naming the id, rather than succeeding over nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::QueueCrudTests::test_an_operation_on_an_absent_charter_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
