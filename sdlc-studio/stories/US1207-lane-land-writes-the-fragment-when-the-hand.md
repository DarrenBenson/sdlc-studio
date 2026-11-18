# US1207: Lane land writes the fragment when the hand-in has none, keeps a hand edit, and the brief names the command

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0676
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py
> **Epic:** EP0329
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Lane land writes the fragment when the hand-in has none, keeps a hand edit, and the brief names the command
**So that** CR0676 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Lane land writes the fragment when the hand-in has none

- **Given** a builder's worktree whose staged change carries no `changelog.d/<unit>.md`
- **When** `sprint.py lane land --worktree <path> --units <id>` is run
- **Then** the landed commit carries `changelog.d/<unit>.md` as `artifact.py changelog <id>` writes it, the landing's output names the file it wrote, and `changelog.py shape` passes it. Fails on: a lane landed with no fragment, or a fragment written to the root after the commit and so left uncommitted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandWritesTheFragmentTests::test_a_hand_in_with_no_fragment_lands_with_a_generated_one

### AC2: A fragment the builder staged is landed as it is

- **Given** a worktree whose staged change carries a hand-edited fragment, and one whose staged fragment is malformed
- **When** `sprint.py lane land` is run for each
- **Then** the first lands with the fragment's bytes exactly as the builder staged them; the second reaches the commit hook unreplaced, where `changelog.py shape --staged` still refuses it and the landing stops at exit 1. Fails on: a hand edit overwritten by the generator, or a malformed fragment silently replaced so the shape lane never judges it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandWritesTheFragmentTests::test_a_staged_fragment_is_kept_and_a_malformed_one_is_still_refused

### AC3: The lane brief names the command, not the format

- **Given** an open run with a Ready unit
- **When** `sprint.py lane brief --units <id>` is run
- **Then** the brief names `artifact.py changelog <id>` as the way to write the unit's fragment and says `lane land` writes it when the hand-in has none, and spells out no section comment or fragment layout. Fails on: a brief that names no command, or teaches the format the builder then learns by reading other fragments
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandWritesTheFragmentTests::test_the_lane_brief_names_the_changelog_command

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
