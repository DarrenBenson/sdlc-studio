# BG1302: `sprint lane brief --units US-01M6XQJF` tells the builder it shares a seam with a nameless unit, because the seam scope keeps the run state's `US01M6XQJF` and the asked-for `US-01M6XQJF` as two units

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1302.md
> **Evidence:** RUN-01M6YSAV lane brief for US-01M6XQJF, 2026-11-09: run-state batch ['US01M6XQJF'], seams[0].units ['US01M6XQJF', 'US01M6XQJF']
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T00:07:03Z

## Summary

`lane_dispatch` (.claude/skills/sdlc-studio/scripts/sprint.py:2628) builds the seam scope as `dict.fromkeys([*approved, *unit_ids])`, deduplicating the raw strings. In a schema-3 project the run state's batch stores the id with its hyphen dropped (`US01M6XQJF`), while the command line names it as written (`US-01M6XQJF`), so both enter the scope. `refine.seam_map` resolves both to the same story and returns a seam whose units are `["US01M6XQJF", "US01M6XQJF"]`, sharing all twelve of its Affects, with the absolute and relative spellings of each path mixed. The rendered brief then prints a `Seam with` line whose list of other units is empty, so the colon follows the word directly, then "you both touch ... NOBODY states what the other must not regress": a one-unit batch is told it has an unowned seam with a unit of no name. Found opening the site's 6.3.0 run (RUN-01M6YSAV) in a consuming project on 2026-11-09.

## Steps to Reproduce

In a schema-3 project, open a run with one story whose id carries a hyphen (`sprint plan --worklist <file> --write`), then run `sprint.py lane brief --units <that id as written> --format json`: `seams` holds one entry whose `units` names the unit twice.

## Proposed Fix

Normalise each id with the same function the run state uses before deduplicating the scope, and have `seam_map` skip a pair whose two ids name the same unit. Pin it with a one-unit schema-3 batch briefed under its hyphenated id: `seams` is empty and the brief prints no `Seam with` line.

## Acceptance Criteria

- [ ] **AC1** `lane_dispatch` (.claude/skills/sdlc-studio/scripts/sprint.py:2628) normalises every id with `sdlc_md.norm_id`, the function the run state uses, before deduplicating the seam scope, so a schema-3 unit the run state holds as `US01M6XQJF` and the command line names as `US-01M6XQJF` enters the scope once.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneSeamScopeTests::test_a_schema3_unit_named_with_its_hyphen_enters_the_scope_once
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: in a schema-3 project with a one-story run opened by `sprint plan --worklist <file> --write`, `sprint.py lane brief --units <that id as written> --format json` prints an empty `seams` list.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_a_one_unit_schema3_batch_briefed_by_its_hyphenated_id_has_no_seam
- [ ] **AC3** No brief reports a seam between a unit and itself: `_batch_seams` drops a seam whose units name one unit under `sdlc_md.norm_id`, so the text brief prints no `Seam with` line for it, while a two-unit schema-3 batch whose stories share a file still names its seam with the other unit by id.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeamBriefTests::test_a_schema3_unit_has_no_seam_with_itself_and_a_real_seam_is_still_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-09 | Claude Opus 5.5 (run nine) | Affects names the unit's changelog fragment, which grooming left out |
