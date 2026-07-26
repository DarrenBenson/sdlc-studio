# US0433: sprint batch drop and add: mutate an open batch, drop releasing the done-gate and distinct from Deferred

> **Status:** Done
> **Delivers:** CR0421
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0162
> **Points:** 3

## User Story

**As an** operator whose sprint did not land exactly as planned
**I want** to drop a unit from an open batch with a recorded reason, and add one in
**So that** the done-gate and sign-off lanes track the batch I am actually delivering, instead of
a day-one list that binds the close forever - without hand-editing the tool's own run-state.json

## Acceptance Criteria

### AC1: dropping a unit removes it from the open batch and records the change

- **Given** an open run whose batch contains a unit
- **When** `sprint batch drop <id> --reason "<text>"` runs
- **Then** the unit leaves `run-state.json`'s `batch`, a `batch_changes` entry records the drop with
  its reason and timestamp, and the done-gate no longer demands the dropped unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::BatchMutationTests::test_drop_removes_unit_and_records_the_change
- **Verified:** yes (2026-07-26)

### AC2: adding a unit puts it in the open batch under the same gates

- **Given** an open run
- **When** `sprint batch add <id>` runs
- **Then** the unit joins `batch`, a `batch_changes` entry records the add, and it is then held to the
  same done-gate as the rest of the batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::BatchMutationTests::test_add_appends_to_open_batch_and_records_the_change
- **Verified:** yes (2026-07-26)

### AC3: dropping is distinct from Deferred in effect

- **Given** two undelivered batch units, one transitioned to `Deferred` and one `batch drop`ped
- **When** the done-gate is evaluated
- **Then** the Deferred unit still blocks (Deferred judges the WORK), while the dropped unit does not
  (drop judges THIS BATCH) - the two are not interchangeable
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::BatchMutationTests::test_drop_releases_the_done_gate_but_deferred_does_not
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
