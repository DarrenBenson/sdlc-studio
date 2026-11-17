# US1219: The review dispatch groups a wave's units of at most 3 points into reviewer batches of at most three

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0680
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0332
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The review dispatch groups a wave's units of at most 3 points into reviewer batches of at most three
**So that** CR0680 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A wave's small units are grouped three to a reviewer

- **Given** a wave of five landed units, four of at most 3 points and one of 5 points
- **When** the wave's review dispatch is asked for through `sprint.py`
- **Then** it emits three dispatches: one of three small units, one of the remaining small unit, and the 5-point unit alone; each dispatch names every one of its units' brief path and verdict path. Fails on: four units given to one reviewer, or the 5-point unit placed in a batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ReviewBatchDispatchTests::test_small_units_are_grouped_three_to_a_reviewer

### AC2: A batch never reaches a reviewer who wrote one of its units

- **Given** a batch of three units built by two different authors
- **When** its dispatch is read
- **Then** it names the author of every unit in the batch and says the reviewer must be none of them, and each unit's verdict is still recorded against its own author. Fails on: a dispatch that names only the first unit's author
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ReviewBatchDispatchTests::test_a_batch_names_every_units_author_as_excluded

### AC3: One unit, or a unit with no points, is dispatched alone and the grouping is stable

- **Given** a wave of one unit, and a wave holding a unit that declares no Points
- **When** the review dispatch is asked for twice for each
- **Then** the single unit gets one dispatch naming its one brief; the unit with no Points is dispatched alone and named as unsized; and both runs give the same batches in the same order. Fails on: an unsized unit treated as small, or batches that change between two runs over one wave
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ReviewBatchDispatchTests::test_a_single_or_unsized_unit_is_alone_and_the_grouping_is_stable

### AC4: The runbook and the sprint reference state the batch rule

- **Given** reference-sprint-toolchain.md and reference-sprint.md
- **When** their sections on dispatching reviewers are read
- **Then** both state the rule: at most three units to a reviewer, each of at most 3 points, one brief and one verdict file for each unit. Fails on: a page that still describes one reviewer for each unit and names no limit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ReviewBatchDispatchTests::test_the_references_state_the_review_batch_rule

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
