# BG0584: the tick-verification checklist row is rung-blind, so a grooming run cannot answer it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_ck_tick_verification` asks whether the tree supports the criteria a unit TICKED. On a `design` rung nothing is ticked and nothing should be: the rung's product is authored criteria that are deliberately RED, and every one is unticked by definition. The row then reports `no ticked criteria found` and holds the close as a compulsory unanswered item, on the reasoning that nothing checked is not the same as everything supported. That reasoning is exactly right for a build rung and structurally unanswerable for a grooming one - there is no action that clears it, because ticking a criterion whose behaviour does not exist is the vacuous-verifier defect the rung exists to catch. Same family as BG0582: a lane that reads no rung and applies the build rung's question to a run that never targeted it.

## Steps to Reproduce

Measured 2026-08-16 on RUN-01M05A5M at 7697ee36, after BG0582's close-chain repair landed. 1. Open a run with `sprint plan --goal design`. 2. Groom every unit, leaving all criteria unticked and red - the rung's stated exit. 3. `sprint.py close --dry-run --retro RETRO0103` reports `STOP checklist: tick-verification: Ticked criteria the tree supports - no ticked criteria found`, detail `none of the 12 unit(s) carries a criterion this row can read, so nothing was checked`, as the single remaining compulsory unanswered item. No sequence of commands clears it. SEPARATELY OBSERVED, and possibly a second defect: in the close run at ba8ac72e the SAME row resolved two different ways within one invocation - `no ticked criteria found` in the chain listing and `diff unreadable` in the unanswered block, the latter naming base ref ba3bffa2c. That base ref resolves (`git cat-file -t` reports `commit`) and `_changed_paths` against it returns 32 paths when called directly, so the `diff unreadable` branch was reached with a context the direct call does not reproduce. Not diagnosed further here.

## Proposed Fix

Make the row rung-aware in the same way `undelivered_blockers` and `_signoff_preflight` now are: read `sprint.run_rung(state)` and, for a non-`done` rung, either report the row as not-applicable with the rung named, or replace it with the question that rung DOES owe - that every criterion is unticked and red, which is the design rung's actual exit condition and is currently checked by nothing. The second shape is preferable: it converts a row that cannot be answered into one that would have caught a criterion ticked before its behaviour existed. Investigate the two-resolutions-in-one-run observation separately before assuming it is the same cause.

## Acceptance Criteria

- [ ] **AC1** Given a run whose rung is `design` and whose units carry only unticked criteria, when the sprint checklist resolves `tick-verification`, then it does NOT report a compulsory unanswered item
- [ ] **AC2** Given a run whose rung is `design` and a unit carrying a TICKED criterion, when the row resolves, then it reports that unit - a design rung ticking a criterion before its behaviour exists is the defect the rung exists to catch
- [ ] **AC3** Given a `done` rung, when the row resolves, then its behaviour is unchanged - the tick-versus-diff comparison still runs and still holds the close

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
