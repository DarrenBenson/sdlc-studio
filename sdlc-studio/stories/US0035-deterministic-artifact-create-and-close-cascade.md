# US0035: deterministic artifact create and close cascade

> **Status:** Done
> **Created:** 2026-06-21
> **Epic:** EP0008

## User Story

**As a** team using SDLC Studio
**I want** one tool to create and wire any numbered artifact
**So that** creation is deterministic instead of a ~10-step hand cascade (CR0045).

## Acceptance Criteria

### AC1: `new` creates + wires + validates any of the 8 numbered types

- **Given** a repo with the type's index
- **When** `artifact new --type T --title ...` runs
- **Then** it writes a valid scaffold (correct vocab status; story has a populated AC section), appends the header-matched index row, recomputes counts, and a story is wired into its epic's Story Breakdown
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::NewTests::test_all_types_scaffold_validates
- **Verified:** yes (2026-06-21)

### AC2: no false wiring - exact ids, escaped pipes, generic rows, degradation

- **Given** odd inputs (a loose epic id, a pipe in the title, an unknown index column, no index)
- **When** `new` runs
- **Then** a loose id never wires the wrong epic, a pipe round-trips, an unknown column is `--` with the row width intact, and a missing index degrades to indexed=False without crashing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::NewTests::test_loose_epic_id_does_not_wire_wrong_epic
- **Verified:** yes (2026-06-21)

### AC3: `close` terminal-transitions by id with the right per-type status

- **Given** an artifact id
- **When** `artifact close --id` runs
- **Then** it maps the prefix to the type, transitions to the per-type terminal status (cascading via transition), and an unknown prefix raises
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::CloseTests
- **Verified:** yes (2026-06-21)

## Implementation

`scripts/artifact.py` (`new` for all 8 numbered types: scaffold + generic header-driven
index row + story->epic cross-link; `close` via transition). Shares `file_finding.append_index_row`
(refactored out, behaviour-preserving). **This story was itself created by `new`** (dogfood).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0045) | Created via `new` (deterministic - dogfood); critic APPROVE after the loose-epic-id HIGH fix |
