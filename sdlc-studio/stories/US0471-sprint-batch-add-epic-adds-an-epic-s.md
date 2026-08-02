# US0471: sprint batch add-epic adds an epic's stories at a named status as one set, priced through the shared renderer

> **Status:** Ready
> **Delivers:** CR0441
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US0471.md
> **Epic:** EP0171
> **Points:** 3

## User Story

**As a** operator pulling a whole epic into a running sprint
**I want** one call that adds the epic's stories at a stated status and prices the set
**So that** bringing an epic in is one decision with one capacity answer, not one blind call per story

## Acceptance Criteria

### AC1: AC1: the epic's stories at a NAMED status are added in one call and priced as a set

- **Given** an open run and an epic holding stories at several statuses
- **When** `sprint.py batch add-epic <EPID> [--status Ready]` runs
- **Then** the selection is `select_batch(kind='story', status=<the named status>, epics={EPID})` - there is no intrinsic 'plannable' set, because `_collect` (sprint.py:1024) applies an epic filter only alongside an explicit status - the status in force is printed, defaults to Ready when the flag is absent, only those stories enter the batch, and the combined points and capacity line come from the shared renderer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::AddEpicTests::test_the_epic_stories_at_the_named_status_are_added_as_a_priced_set
- **Verified:** yes (2026-08-02)

### AC2: AC2: the selection tracks the epic, proven against a MUTATED fixture rather than a second identical call

- **Given** an epic whose story set is changed on disk between two invocations - a new story at the selected status is written into the epic after the first call
- **When** `add-epic` is run again for the same epic on the mutated tree
- **Then** the newly written id is in the batch and the selected set equals `select_batch` for the same epic scope on the mutated tree; a story written at a DIFFERENT status is absent. Comparing one call against another with identical arguments could not go red, so the fixture is mutated between them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::AddEpicTests::test_a_story_added_to_the_epic_between_calls_is_picked_up_and_a_wrong_status_one_is_not
- **Verified:** yes (2026-08-02)

### AC3: AC3: units already in the batch are named and not double counted

- **Given** an open run already holding one of the epic's selected stories
- **When** `add-epic` runs for that epic
- **Then** the batch holds each id exactly once, the output names the already-present unit, and the reported points added count only the units actually added
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::AddEpicTests::test_already_present_units_are_named_and_not_double_counted
- **Verified:** yes (2026-08-02)

### AC4: AC4: an epic with nothing at that status fails loud and changes nothing

- **Given** an open run and an epic with no story at the selected status
- **When** `add-epic` runs for it
- **Then** it exits non-zero naming the epic and the status it looked for, run-state.json is byte-identical, and no batch_changes entry is written - no successful empty add
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::AddEpicTests::test_an_epic_with_nothing_at_that_status_fails_loud_and_changes_nothing
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
