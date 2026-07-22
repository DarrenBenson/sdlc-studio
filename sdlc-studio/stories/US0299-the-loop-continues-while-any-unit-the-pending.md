# US0299: The loop continues while any unit the pending question does not block remains

> **Status:** Done
> **Delivers:** CR0378
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0099
> **Points:** 5

## User Story

**As a** sprint operator
**I want** the loop to keep building every unit a pending question does not block, and to refuse
its own stop while such a unit remains
**So that** one undecidable unit costs one unit of progress rather than the whole batch

## Acceptance Criteria

### AC1: deferring names the units the batch continues with

- **Given** an open run whose batch holds one unit that needs an operator decision and others
  that do not
- **When** `sprint decision defer --unit <id> --question "..." --option "a|..." --option "b|..."`
  runs
- **Then** the deferral is recorded and the command names the remaining units the batch
  continues with, not only the count of pending decisions
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_defer_names_the_units_the_batch_continues_with
- **Verified:** yes (2026-07-22)

### AC2: an agent-initiated stop with unblocked work remaining is refused

- **Given** at least one pending decision and at least one batch unit that none of the pending
  questions blocks
- **When** the run attempts to stop
- **Then** the stop is refused with a non-zero exit, names the unblocked units, and names
  `sprint decision defer` as the path that keeps the batch moving
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_a_stop_with_unblocked_work_remaining_is_refused
- **Verified:** yes (2026-07-22)

### AC3: the stop is allowed only when nothing can proceed

- **Given** a batch in which every remaining unit is a deferred unit or a declared dependant of
  one
- **When** the run attempts to stop
- **Then** the stop is allowed, because the situation is unresolvable rather than merely
  undecided
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_a_stop_is_allowed_when_no_unit_can_proceed
- **Verified:** yes (2026-07-22)

### AC4: the blocked set is derived, never assumed to be the batch

- **Given** a deferred unit and a sibling that declares no `Depends on:` edge to it
- **When** the blocked set is computed for the pending question
- **Then** the sibling counts as unblocked: only the deferred unit and its declared dependants
  are blocked by that question
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_only_the_deferred_unit_and_its_dependants_are_blocked
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0378 speaks only of the pending question, not of file collisions. Whether a shared-file
  cluster (`_shared_file_clusters`) should also count a unit as blocked by a deferred decision
  is unstated - Owner: operator
- [ ] Which surface performs the refused stop is unstated. CR0378 names "an agent-initiated
  stop"; `sprint.py` already carries `_boundary_stop` and `loop_guard` carries the budget exit,
  and the request does not say whether one, both or a new stop entry point is in scope -
  Owner: implementer

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and ACs authored against CR0378 |
