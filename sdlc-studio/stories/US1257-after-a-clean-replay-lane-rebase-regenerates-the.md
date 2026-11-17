# US1257: After a clean replay, lane rebase regenerates the script surface page and re-stages it, naming any derived page left stale

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0707
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase_derived.py
> **Epic:** EP0347
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** After a clean replay, lane rebase regenerates the script surface page and re-stages it, naming any derived page left stale
**So that** CR0707 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A clean replay regenerates the script surface page and re-stages it

- **Given** a lane whose staged change adds a flag to a shipped script and regenerates `reference-scripts-surface.md`, and a main that has since landed another script's flag on the same page
- **When** `sprint.py lane rebase --worktree <path>` replays the lane cleanly
- **Then** the staged surface page is byte-identical to what `docgen.py` generates from the rebased tree, carrying both flags, and it is staged. Fails on: a surface page left as the lane or main wrote it, missing one of the two flags, or regenerated but not staged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase_derived.py::LaneRebaseDerivedTests::test_the_surface_page_is_regenerated_from_the_rebased_tree_and_staged

### AC2: A derived page it does not regenerate is named when the replay leaves it stale

- **Given** a clean replay after which a derived page the command does not write (the command audit, or the root census totals) no longer matches the rebased tree
- **When** the command finishes
- **Then** its output names each stale page with the command that regenerates it, and names none when every derived page is current. Fails on: a stale command audit passed over in silence, so the lane's commit is refused later by a hook, or a current page reported stale
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase_derived.py::LaneRebaseDerivedTests::test_a_stale_derived_page_is_named_with_its_command

### AC3: Nothing is regenerated after a conflict or where no surface page exists

- **Given** one replay that stops on a conflict, and one clean replay in a project that ships no `reference-scripts-surface.md`
- **When** `sprint.py lane rebase --worktree <path>` is run on each
- **Then** the conflicted worktree has no derived page written or staged by the command, and the project without the page replays cleanly, exits 0 and says the regeneration was skipped. Fails on: a page generated over a conflicted tree, or a consuming project failed for a page it does not have
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_rebase_derived.py::LaneRebaseDerivedTests::test_no_regeneration_after_a_conflict_or_without_a_surface_page

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
