# US1206: An artifact changelog command writes a unit's fragment in the shape the changelog-shape lane passes

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0676
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0329
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** An artifact changelog command writes a unit's fragment in the shape the changelog-shape lane passes
**So that** CR0676 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The command writes a fragment the shape lane passes unedited

- **Given** a scratch project with a Ready story and an Open bug, each with a title and three authored acceptance criteria
- **When** `artifact.py changelog <id>` is run for each, then `changelog.py shape` over the files it wrote
- **Then** `changelog.d/<id>.md` exists for each, its first line a section comment the lane knows (Fixed for the bug), its entry built from the unit's title and each criterion's headline, and the shape check exits 0 on both with no edit made. Fails on: a fragment the changelog-shape lane refuses, or an entry carrying text that is in neither the title nor a criterion
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ChangelogFragmentTests::test_the_generated_fragment_passes_the_shape_check_unedited

### AC2: A fragment already there is kept

- **Given** a `changelog.d/<id>.md` the command wrote, then edited by hand
- **When** `artifact.py changelog <id>` is run again
- **Then** the file's bytes are the hand-edited ones and the command says the fragment exists and was kept. Fails on: a second run that overwrites the author's edit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ChangelogFragmentTests::test_a_hand_edited_fragment_is_kept_on_a_second_run

### AC3: A unit with nothing to write from is refused

- **Given** an id no artefact carries, and a story whose Acceptance Criteria section is still the grooming placeholder
- **When** `artifact.py changelog <id>` is run for each
- **Then** each exits 2 naming why and writes no file; a groomed story in the same project still gets its fragment. Fails on: an empty or placeholder fragment written for a unit with no criteria
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ChangelogFragmentTests::test_an_unknown_or_ungroomed_unit_is_refused_and_nothing_is_written

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
