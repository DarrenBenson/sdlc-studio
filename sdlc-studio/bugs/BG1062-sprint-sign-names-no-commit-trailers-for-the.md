# BG1062: sprint sign names no commit trailers for the paperwork it writes, so its commit draws one engagement-floor attribution advisory per unit it moved

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_names_its_trailers.py, changelog.d/BG1062.md
> **Evidence:** RUN-01M4R168 sign commit 2dd360a1, 2026-10-16: the commit-msg hook printed `attribution note (advisory - the commit is not blocked)` with one `engagement floor (attribution)` line for each of the 18 units the sign moved (BG0944, BG0945, BG0950, BG0976, ...).
> **Created:** 2026-10-18
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-18T18:42:25Z

## Summary

`sprint sign` moves every batch unit to its terminal status and tells the operator to commit the result, but never names the `Refs:` trailers that commit needs. The commit-msg hook's engagement-floor attribution then prints an advisory for each staged unit file whose id the message does not name. RUN-01M4R168's sign commit (2dd360a1) drew 18 of them, one per unit moved, and the advisories bury anything else the hook prints.

Reproduced at cecc9dfe7 (2026-11-24): `cmd_sign` and `_seal_units` print no `Refs:` line, and `engagement_floor.unnamed_unit_attribution` over two staged bug files moved to Fixed, under a message naming a third bug, returns one note per moved bug. The seal moves only units not already terminal, and a unit accepted through `sprint lane accept` is moved there, so the sign commits of runs eighteen to twenty-four staged no unit file; a run whose units were not accepted through a lane still meets it. A message naming no judged unit (only the RUN and RPT ids) draws no advisory at all, so the noise arrives when the sign commit also names a bug or story.

## Steps to Reproduce

1. `sprint.py sign --report RPTxxxx --principal <operator>` on a run with N units. 2. Commit the paperwork with a message naming the report and one other unit, for example a bug filed in the same commit (`Refs: RPTxxxx`, `Refs: BGxxxx`). 3. The commit hook prints `engagement floor (attribution): this commit stages sdlc-studio/bugs/<id>-....md ... the message never names <id>` N times.

## Proposed Fix

Have `sign` print, after it seals, the trailer block its paperwork commit needs: one `Refs: <id>` per unit `_seal_units` moved, and none for a unit already terminal or one the retro carries (its ids are the walk's own `pending` list). A seal that moves nothing prints no block. The attribution lane in `engagement_floor.py` is left as it is.

## Acceptance Criteria

- [ ] **AC1** Given a run whose seal moves one story to Done and one bug to Fixed, and a third unit already terminal, when `sprint sign` seals it, then its stdout carries one trailer block naming exactly `Refs: <id>` for the two units it moved. Fails on: the sign printing no trailer at all, so the operator has to work the ids out from the batch.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_names_its_trailers.py::SignNamesItsTrailersTests::test_sign_prints_a_refs_trailer_per_unit_it_moved
- [ ] **AC2** Given the moved units' files staged in a git fixture and a commit message naming another bug, when `engagement_floor.unnamed_unit_attribution` reads that message with the printed trailers appended, then it returns no note for a moved unit, and the same message without them (the control) returns one note per moved unit. Fails on: one `engagement floor (attribution)` advisory per unit the sign moved.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_names_its_trailers.py::SignNamesItsTrailersTests::test_the_printed_trailers_satisfy_the_attribution_advisory
- [ ] **AC3** Given a run whose every unit is already terminal before the sign, when `sprint sign` seals it, then it prints no trailer block and no bare `Refs:` line. Fails on: a mutant printing the whole batch, or an empty block, as the trailers.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_names_its_trailers.py::SignNamesItsTrailersTests::test_a_seal_that_moves_nothing_prints_no_trailers

## Impact

Advisory noise on a sign commit that moves units and names another unit, proportional to the units moved; a real attribution gap in the same commit is easy to miss.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-18 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe7; three executable criteria (the trailer block, the advisory it answers, the no-move boundary); Affects drops test_sprint.py; Points 1 to 2 for the git-staged fixture |
