# US0487: A sprint charter is a first-class artefact: goal, scope rule and appetite, with a tool-allocated id and an index row

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0176
> **Points:** 5

## User Story

**As a** maintainer building the queue on the same footing as every other artefact
**I want** a sprint charter to be a real artefact carrying its goal, scope rule and appetite
**So that** a charter a second person must judge has an id, a history and an index row rather than being a line in a file

## Acceptance Criteria

### AC1: a charter is created with a tool-allocated id and an index row

- **Given** a workspace with a sprints directory and its index
- **When** a charter is created carrying a goal, a scope rule and an appetite
- **Then** it is written with an allocated id, its index row is appended, and no id is ever hand-authored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SprintCharterTests::test_a_charter_is_minted_with_an_allocated_id_and_index_row

### AC2: a charter missing the parts a run needs is refused at creation

- **Given** a charter request with no goal, or no scope rule
- **When** creation runs
- **Then** it is refused naming what is absent, because a charter nobody can materialise is not a charter
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SprintCharterTests::test_a_charter_without_a_goal_or_scope_is_refused

### AC3: the charter's status vocabulary is derived, not restated at the call site

- **Given** the shared status vocabulary
- **When** a charter moves between states
- **Then** the permitted states come from the shared vocabulary rather than a set written beside the charter code, so the two cannot disagree about what queued or spent means
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SprintCharterTests::test_the_status_vocabulary_is_derived_from_the_shared_source

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
