# BG0584: the tick-verification checklist row is rung-blind, so a grooming run cannot answer it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, sdlc-studio/decisions.md
> **Verification depth:** functional (four of the five criteria drive the real checklist resolver over a temp corpus at four rungs; AC4 drives NO resolver and says so - it asserts this repository's own decisions log, after asserting the log parsed to rows - the earlier form `assertIsNotNone(x or list_decisions(repo))` CANNOT fail, because `[] is not None`, and a review found it. Mutation: 7 declared Test Plan rows across the 5 criteria - AC2 and AC5 carry two each - of which `run --from-plan` joins 5, one per criterion, because `_testplan_rows` keys by criterion and silently drops a second row on the same AC. Every row was executed. Each anchor asserted unique, `__pycache__` purged and `python3 -B`, all 8 KILLED, restore byte-exact, all KILLED - including one that leaves D0144 ACCEPTED, and one scoping the rung test back to `!= "done"`, which is what round 1 REJECTED this unit for)
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_ck_tick_verification` asks whether the tree supports the criteria a unit TICKED. On a `design` rung nothing is ticked and nothing should be: the rung's product is authored criteria that are deliberately RED, and every one is unticked by definition. The row then reports `no ticked criteria found` and holds the close as a compulsory unanswered item, on the reasoning that nothing checked is not the same as everything supported. That reasoning is exactly right for a build rung and structurally unanswerable for a grooming one - it cannot be ANSWERED, only waived - `decisions.py waive --subject rule:sprint-checklist:tick-verification` clears it and the row prints that command as its own remedy, so the defect is a ceremony tax every design run pays forever, not a wall. Same family as BG0582: a lane that reads no rung and applies the build rung's question to a run that never targeted it.

## Steps to Reproduce

Measured 2026-08-16 on RUN-01M05A5M at 7697ee36, after BG0582's close-chain repair landed. 1. Open a run with `sprint plan --goal design`. 2. Groom every unit, leaving all criteria unticked and red - the rung's stated exit. 3. `sprint.py close --dry-run --retro RETRO0103` reports `STOP checklist: tick-verification: Ticked criteria the tree supports - no ticked criteria found`, detail `none of the 12 unit(s) carries a criterion this row can read, so nothing was checked`, as the single remaining compulsory unanswered item. A waiver clears it (D0144 did, the same day), but nothing ANSWERS it - so every design run must waive the same row, which trains the operator to waive. SEPARATELY OBSERVED, now DIAGNOSED and split out as BG0593 (`close_dry_run` copies only `sdlc-studio/` so the scratch tree has no `.git`): in the close run at ba8ac72e the SAME row resolved two different ways within one invocation - `no ticked criteria found` in the chain listing and `diff unreadable` in the unanswered block, the latter naming base ref ba3bffa2c. That base ref resolves (`git cat-file -t` reports `commit`) and `_changed_paths` against it returns 32 paths when called directly, so the `diff unreadable` branch was reached with a context the direct call does not reproduce. Not diagnosed further here.

## Proposed Fix

Make the row rung-aware in the same way `undelivered_blockers` and `_signoff_preflight` now are: read `sprint.run_rung(state)` and, for a non-`done` rung, either report the row as not-applicable with the rung named, or replace it with the question that rung DOES owe - that every criterion is unticked and red, which is the design rung's actual exit condition and is currently checked by nothing. The second shape is preferable: it converts a row that cannot be answered into one that would have caught a criterion ticked before its behaviour existed. Investigate the two-resolutions-in-one-run observation separately before assuming it is the same cause.

## Acceptance Criteria

- [x] **AC1** Given a run whose rung is `design`, when `_ck_tick_verification` resolves, then the rung is read BEFORE the base-ref and diff branches - both return NOT_RUN first, and the real close resolved this row as `diff unreadable`, so a rung check placed at `not examined` passes a fixture and leaves the observed wall standing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationReadsTheRungTests::test_the_rung_is_read_before_the_diff_branches
  - **Verified:** yes (2026-08-18)
- [x] **AC2** Given a `design` rung and a unit carrying a TICKED criterion, when the row resolves, then it reports that unit as a NON-BLOCKING row - `checklist` is not in `_DEFERRABLE_CLOSE_STAGES`, so a blocking row here would be a hard refusal with no bounded exit, which is the shape this unit exists to remove.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationReadsTheRungTests::test_a_ticked_criterion_on_a_design_rung_is_reported_not_blocking
  - **Verified:** yes (2026-08-18)
- [x] **AC3** Given a `done` rung, when the row resolves, then its behaviour is byte-identical to today - AND SO IS a `plan` or `triage` rung's. Those are non-build rungs whose product is NOT grooming: `--goal plan` selects, sequences and estimates already-groomed units, so scoping this fix on `!= "done"` switches the gate off for them and MOVES the defect one rung over rather than closing it. That is what round 1 rejected, and it is the second time this repository has made the same mistake - `sprint.py` records the identical ruling twice in the sibling readers.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationReadsTheRungTests::test_the_build_rung_is_unchanged
  - **Verified:** yes (2026-08-18)
- [x] **AC4** Given this repository with D0144 RETRACTED, when the sprint checklist is re-run over RETRO0103, then `tick-verification` resolves without a waiver - a fix landing under a live waiver is a fix nobody can observe, because the row reads WAIVED whether it is fixed or not.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationReadsTheRungTests::test_the_row_resolves_without_the_waiver
  - **Verified:** yes (2026-08-18)
- [x] **AC5** Given a `design` rung whose batch names units that resolve to no file, when the row reports, then it REFUSES rather than reporting every criterion unticked - a pass over nothing is not a pass, which is the rule the build-rung branch twenty lines below states in terms while the first cut of this helper broke it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TickVerificationReadsTheRungTests::test_a_design_rung_over_unreadable_units_is_not_a_pass
  - **Verified:** yes (2026-08-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
| 2026-08-18 | sdlc-studio | Fixed. `Affects` corrected to name `sdlc-studio/decisions.md`: AC4's exit is the RETRACTION of D0144, so the file the fix must change was outside the scope bounding its own review diff - the same defect BG0590's filing recorded, met again one unit later |
| 2026-08-18 | sdlc-studio | Round 1 REJECT repaired: the fix was scoped `!= "done"` and so moved the defect onto `plan` and `triage` - the identical error BG0582's siblings were rejected for, with the correct ruling already written twice in `sprint.py`. Scoped to `design`. AC5 added: the helper reported every criterion unticked having opened zero files. AC4's second assertion could not fail |

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | delete the rung short-circuit from `_ck_tick_verification`, so the base-ref and diff branches are reached first | Given a run whose rung is `design`, when `_ck_tick_verification` resolves, then the rung is read BEFORE the base-ref and diff branches. |
| AC2 | return `NOT_RUN` instead of `RAN` for a tick found on a non-build rung | Given a `design` rung and a unit carrying a TICKED criterion, when the row resolves, then it reports that unit as a NON-BLOCKING row. |
| AC3 | scope the rung test back to `!= "done"`, switching the gate off for `plan` and `triage` too - the round-1 REJECT, and the second time this repo has made it | Given a `done` rung, when the row resolves, then its behaviour is byte-identical to today. |
| AC4 | flip D0144 back to `accepted` in the decisions log, leaving the waiver live | Given this repository with D0144 RETRACTED, when the sprint checklist is re-run over RETRO0103, then `tick-verification` resolves without a waiver. |
| AC2 | drop the unit ids from the ticked-on-a-design-rung detail | A row that says something is wrong without saying WHAT cannot be acted on. |
| AC5 | report `RAN` when no unit artefact resolved, so an unreadable batch reads as a clean design rung | Given a `design` rung whose batch names units that resolve to no file, when the row reports, then it REFUSES. |
| AC5 | count units rather than files actually opened, so `read` is never incremented | The count must be of artefacts READ, not of ids named. |
