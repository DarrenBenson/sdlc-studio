# BG1336: The lane brief's verify_ac step writes into the unit's own artefact outside its Affects, and lane land's rebase then fails on that unstaged edit while exiting 0 under a pipe

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1336.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md
> **Evidence:** RUN-01M77177, 2026-11-12: BG1010, BG1030 and US1149 lands
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:18:31Z

## Summary

Every lane brief tells the builder to run `verify_ac.py run --id <unit>`, which writes 'Verified' lines and ticks into the unit's story or bug file. That file is outside the unit's Affects, so a builder rightly leaves it unstaged, and `sprint lane land` then cannot rebase ('cannot rebase: You have unstaged changes', 'Conflicting files: none reported').

## Steps to Reproduce

Build a unit, run `verify_ac` in its worktree as the brief says, stage the Affects, run `sprint lane land`: the rebase fails.

## Proposed Fix

Have the brief run `verify_ac` in a mode that does not write the artefact, or have lane land restore that one file before it rebases.

## Acceptance Criteria

- [ ] **AC1** Given a lane worktree whose only unstaged change is `verify_ac`'s edit to the unit's own artefact, when `sprint lane land` runs, then it lands the staged Affects (discarding or carrying that edit as the main tree's verify will rewrite it) instead of refusing the rebase. Fails on: the land refused with 'cannot rebase: You have unstaged changes'.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_verify_acs_artefact_edit_does_not_block_the_land
  - **Verified:** yes (2026-11-13)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-12 | Claude Opus 5.5 (run eleven orchestrator) | At-HEAD triage (D0469): live; Affects gains templates/agents/sdlc-builder.md, which still tells a builder to run verify_ac in its worktree |
