# BG1303: `sprint lane brief` names a schema-3 unit's hand-in files by its normalised id (US01M6XQJF-claims.json) while `lane land --units US-01M6XQJF` reads them by the id as typed, so the self-check is never recorded at landing

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M6YSAV, 2026-11-09: lane land output for US-01M6XQJF at 37139ea; the brief's hand-in names US01M6XQJF-claims.json and US01M6XQJF-mutants.json
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T00:54:02Z

## Summary

The lane brief's hand-in names come from `_lane_hand_in_files(uid)` (.claude/skills/sdlc-studio/scripts/sprint.py:2809-2811) with the brief's id, which for a schema-3 unit is the normalised form with the hyphen dropped (`US01M6XQJF`). `lane land` looks for `keep / f"{unit}-claims.json"` (.claude/skills/sdlc-studio/scripts/lib/lanes.py:200), where `unit` is the id as the command line spelt it (`US-01M6XQJF`). A builder that follows its brief therefore hands in files land does not read. On 2026-11-09, in a consuming project's site run (RUN-01M6YSAV), land committed and fast-forwarded the unit and then printed "self-check NOT RECORDED and no brief written - the hand-in carries no US-01M6XQJF-claims.json or US-01M6XQJF-mutants.json". The self-check had to be recorded by hand with `critic.py self-check record` from the copied hand-in, and the QA brief written by hand. Under `review.author_self_check: block`, missing that line means `critic.py brief` refuses the unit. BG1296 (the brief path keyed by the raw id's case) and BG1302 (the seam scope keeping both spellings) are the same family: each site keys a unit by a different spelling of its id.

## Steps to Reproduce

In a schema-3 project, open a run with a story whose id carries a hyphen, run `sprint.py lane brief --units <id as written>`, and note the hand-in names it prints (no hyphen). Hand in those files from a lane worktree, then run `sprint.py lane land --worktree <wt> --units <id as written>`: the unit lands and the self-check is not recorded.

## Proposed Fix

Key every lane file (hand-in names, brief path, land's lookup) by `sdlc_md.norm_id`, or have land accept either spelling and say which it read. Pin it with a schema-3 hyphenated unit landed through the brief's own hand-in names: the self-check is recorded and the QA brief written.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The lane brief's hand-in names come from `_lane_hand_in_files(uid)` (.claude/skills/sdlc-studio/scripts/sprint.py:2809-2811) with the brief's id, which for a...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a schema-3 project, open a run with a story whose id carries a hyphen, run `sprint.py lane brief --units <id as written>`, and note the hand-in names it...
- [ ] **AC3** The proposed fix lands, pinned by a test: Key every lane file (hand-in names, brief path, land's lookup) by `sdlc_md.norm_id`, or have land accept either spelling and say which it read.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
