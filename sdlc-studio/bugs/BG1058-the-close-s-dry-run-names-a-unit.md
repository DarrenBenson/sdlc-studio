# BG1058: The close's dry run names a unit the run cannot end over that the real tree answers

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_dry_run_read_root.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1058.md
> **Evidence:** close --dry-run on 2026-10-15 at cd618e90 (scratchpad log) against the direct predicate's [] on the same tree.
> **Created:** 2026-10-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-15T20:47:29Z

## Summary

On RUN-01M4R168, `sprint.py close --retro RETRO0134 --dry-run` reported 'known-issues: 1 batch unit(s) the run cannot end over: BG0978 (Open) - unfinished and not ruled'. Read against the real tree at the same moment, `sprint.unanswered_units(root`, state, 'RETRO0134') returned [] and `seal_bar_unmet(`'BG0978') returned [] (BG0978 approved, coverage approved). The dry run judges a scratch copy holding only sdlc-studio/, so some probe behind the predicate reads that copy where it should read the real tree (the `read_root` the checklist context carries). A false refusal in the preview sends the operator to rule or drop a unit that needs nothing.

## Steps to Reproduce

With an approved bug in the open run's batch, compare `sprint.py close --retro <id> --dry-run`'s known-issues line with `sprint.unanswered_units` on the real tree: the dry run names the unit, the predicate does not.

## Proposed Fix

Find which probe under `unanswered_units` or `seal_bar_unmet` reads the scratch root (a file outside sdlc-studio/, such as a unit's Affects or a test module, read for its band or coverage) and route it through `read_root`, then pin the preview against the live predicate on one fixture.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose every batch unit meets the seal bar on the real tree, when `sprint.py close --dry-run` runs, then its known-issues line names no unit the live predicate answers
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_dry_run_read_root.py::DryRunReadRootTests::test_the_dry_run_names_no_unit_the_live_predicate_answers

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-15 | sdlc-studio | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
