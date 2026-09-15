# BG0661: revert-check never names the units it set aside, and once one unit is examined their count vanishes from the lane line too

> **Status:** Fixed
> **Verification depth:** functional [[derived: criteria 5; plan rows 11; executed 11; killed 11; survived 0; not-run 0; entry point 1 of 5 criteria through the shipped CLI, 4 in-process | fp 95d2a4aa84c6 ]]
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Boundary run 2026-09-10 on commit 24401fea: revert-check 15.7s, 10 unit(s) examined, none stayed green without its change. Hand check the same morning: reverting the sweep comparisons in DryRunScratchParityTests leaves 11 of 11 green. Two independent review seats reached the same finding on BG0601.
> **Created:** 2026-09-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Narrowed on 2026-09-15 (see Revision History). As filed, this said the lane COUNTS a unit whose Affects names only test files as examined and reports it green, overstating the yield. A fixture at HEAD refutes that half: `verify_ac.revert_check` sets such a unit aside with status `reported` ("Affects names no production file ... REPORTED rather than passed") and `gate._revert_check` never adds it to `examined` - the path has existed since 3bf71833 and BG0640, before this was filed. What stands is what a reader of the boundary output can see. The lane counts the set-aside units (`reported`, and `error` for units it could not measure) but NEVER names them by id, and once at least one unit was examined the detail line becomes "N unit(s) examined, none stayed green without its change" and drops even their counts, which print only on the zero-examined path. So BG0601 - a test-only unit - vanished from the 2026-09-10 boundary line without trace, which is why two seats and a hand check had to find it. CR0511 finding #30 is the same defect and is folded in here. Whether a test-only unit can be revert-checked at all needs a hunk-level revert: that is CR0533/US0754's, not this bug's.

## Steps to Reproduce

1. In a throwaway workspace with an open run and a base ref, batch two units: one whose Affects names a production file and its test, one whose Affects names only a test file.
2. Run the revert-check lane (`gate._revert_check`, or `gate.py --boundary push --only revert-check`).
3. Read the line: "1 unit(s) examined, none stayed green without its change" - the test-only unit is not named, and its `reported` count is not shown.

## Proposed Fix

Name every set-aside unit by id, with its reason (`reported` or `error`), on every path - beside an examined count as well as in place of one. Keep the examined count exclusive of them, as it is today.

## Acceptance Criteria

The rendered form each criterion reads is `<uid> (reported)` for a unit `verify_ac.revert_check` set aside as reported, and `<uid> (error` (optionally followed by the unit's first error text, then `)`) for one it could not measure - the id and its reason in one parenthesised token, so an id printed without its reason, or with the other reason, does not match.

- [ ] **AC1** With one unit examined and clean and one test-only unit in the batch, the revert-check lane's line still leads with `1 unit(s) examined` and names the test-only unit as `<uid> (reported)`, while the examined unit's id carries no set-aside token
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckSetAsideUnitsTests::test_a_reported_unit_is_named_beside_an_examined_one
  - **Verified:** yes (2026-09-15)
- [ ] **AC2** With the examined unit REFUSED (green after the revert) and one test-only unit beside it, the line `gate.py --boundary push --only revert-check` prints on a two-unit fixture workspace names the refused unit as today and ALSO names the test-only unit as `<uid> (reported)`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckSetAsideUnitsTests::test_a_reported_unit_is_named_beside_a_refused_one
  - **Verified:** yes (2026-09-15)
- [ ] **AC3** With one unit examined and one unit the check could not measure, the line names the errored unit as `<uid> (error` and never as `<uid> (reported)`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckSetAsideUnitsTests::test_an_errored_unit_is_named_beside_an_examined_one
  - **Verified:** yes (2026-09-15)
- [ ] **AC4** On the two paths no criterion above reaches - zero units examined (one reported, one errored), and one unit whose check crashed beside one examined unit and one reported unit - the line names every set-aside unit by id with its reason, and the zero-examined line still leads with `no unit was examined`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckSetAsideUnitsTests::test_set_aside_units_are_named_on_the_absence_and_crash_paths
  - **Verified:** yes (2026-09-15)
- [ ] **AC5** Over a batch of one clean unit, one reported unit and one errored unit, the examined figure handed to `_record_revert_yield` is exactly 1 and the line leads with `1 unit(s) examined` - the paired control, true today; it asserts the recorder's argument, never a substring that `11 unit(s)` would also carry
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckSetAsideUnitsTests::test_set_aside_units_are_not_counted_examined
  - **Verified:** yes (2026-09-15)

## Impact

The lane's promotion from advisory to blocking will be decided on what its boundary output shows. A reader of that line cannot see which units the method set aside rather than judged, so a blind spot the lane already knows about - every test-only unit - reaches nobody until a reviewer rediscovers it by hand, as BG0601 was.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, add the set-aside ids only to the zero-examined `absence` string, leaving the `elif examined:` branch's detail as the bare "N unit(s) examined, none stayed green" line | With one unit examined and clean and one test-only unit in the batch, the revert-check lane's line still leads with `1 unit(s) examined` and names the test-only unit as `<uid> (reported)`, while the examined unit's id carries no set-aside token |
| AC1 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, append the bare uid to the set-aside list and print it as "set aside: US0002", dropping the `res["status"]` reason from the token | With one unit examined and clean and one test-only unit in the batch, the revert-check lane's line still leads with `1 unit(s) examined` and names the test-only unit as `<uid> (reported)`, while the examined unit's id carries no set-aside token |
| AC1 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, append every batch uid to the set-aside list before the status test, so the examined unit is printed with a `(reported)` token too | With one unit examined and clean and one test-only unit in the batch, the revert-check lane's line still leads with `1 unit(s) examined` and names the test-only unit as `<uid> (reported)`, while the examined unit's id carries no set-aside token |
| AC2 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, add the set-aside tokens only inside the `if not refused:` block, leaving the refused-path `detail = f"{examined} examined, {len(refused)} would be refused - "` line built as today | With the examined unit REFUSED (green after the revert) and one test-only unit beside it, the line `gate.py --boundary push --only revert-check` prints on a two-unit fixture workspace names the refused unit as today and ALSO names the test-only unit as `<uid> (reported)` |
| AC2 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, replace `_first_three(named)` on the refused path with `_first_three(set_aside)`, so the refused unit's "green after the revert" finding is lost | With the examined unit REFUSED (green after the revert) and one test-only unit beside it, the line `gate.py --boundary push --only revert-check` prints on a two-unit fixture workspace names the refused unit as today and ALSO names the test-only unit as `<uid> (reported)` |
| AC3 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, append the uid to the set-aside list only when `res["status"] == "reported"`, so an `error` unit is still counted in `skipped` but never named | With one unit examined and one unit the check could not measure, the line names the errored unit as `<uid> (error` and never as `<uid> (reported)` |
| AC3 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, hard-code the token's reason as "reported" for every set-aside unit instead of reading `res["status"]` | With one unit examined and one unit the check could not measure, the line names the errored unit as `<uid> (error` and never as `<uid> (reported)` |
| AC4 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, add the set-aside tokens on the `elif examined:` and refused branches only, leaving the `absence` string with its bare "(N reported, N in error)" counts | On the two paths no criterion above reaches - zero units examined (one reported, one errored), and one unit whose check crashed beside one examined unit and one reported unit - the line names every set-aside unit by id with its reason, and the zero-examined line still leads with `no unit was examined` |
| AC4 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, set the crashed branch's `tail = f"{examined} examined and clean"` without the set-aside tokens, so a run with a crash names its reported unit nowhere | On the two paths no criterion above reaches - zero units examined (one reported, one errored), and one unit whose check crashed beside one examined unit and one reported unit - the line names every set-aside unit by id with its reason, and the zero-examined line still leads with `no unit was examined` |
| AC5 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, delete the `continue` after `skipped[res["status"]] += 1`, so a reported or errored unit falls through to `examined += 1` | Over a batch of one clean unit, one reported unit and one errored unit, the examined figure handed to `_record_revert_yield` is exactly 1 and the line leads with `1 unit(s) examined` - the paired control, true today; it asserts the recorder's argument, never a substring that `11 unit(s)` would also carry |
| AC5 | in .claude/skills/sdlc-studio/scripts/gate.py `_revert_check`, change the set-aside test to `res.get("status") == "reported"`, so an `error` unit falls through to `examined += 1` while a reported one is still skipped | Over a batch of one clean unit, one reported unit and one errored unit, the examined figure handed to `_record_revert_yield` is exactly 1 and the line leads with `1 unit(s) examined` - the paired control, true today; it asserts the recorder's argument, never a substring that `11 unit(s)` would also carry |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-10 | Claude Opus 5 | Filed |
| 2026-09-10 | Claude Opus 5 | Ruled OPEN for v5.1 on 2026-09-10, under D0186's disclosure half. revert-check is an ADVISORY lane whose yield is still being measured, so a blind spot in it holds nothing back and misleads nobody: the boundary run records what it examined and this bug names, by id, the class it cannot see - a unit whose production change and its evidence live in one file, which is every test-only unit. Two independent seats reached it on BG0601 and a hand check confirmed 11 of 11 green after the revert. Fixing it means deciding what 'production file' means for a unit that only adds tests, which is a design question and not a patch. |
| 2026-09-15 | sdlc-studio | Retitled: was 'revert-check cannot see a unit whose fix and evidence share one file - it reverts the tests with the change and reports green' |
| 2026-09-15 | sprint planning 2026-09-15 | Groomed for the next batch and NARROWED: the filed mechanism (a test-only unit counted as examined and reported green) is refuted by a fixture at HEAD - such a unit is set aside as reported and never counted. Retitled to the residue: set-aside units are never named by id, and their count vanishes once one unit is examined. CR0511 finding #30 is the same defect, folded in here. Real criteria replace the tool-derived one; 3 -> 2 points. |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan review r1 REJECT answered. The criteria now pin one rendered token, the uid with its reason in parentheses, so an id printed without its reason or with the other reason fails. New AC2 drives the shipped gate.py --boundary push --only revert-check on a two-unit fixture with the examined unit REFUSED, killing a build that names set-aside units only on the no-refusal branches (the reviewer's probe showed the refused line built separately and naming only the refused unit). AC1 gains rows for an id without its reason and for every unit tagged. AC3 (was AC2) gains the hard-coded reported mutant. New AC4 pins the zero-examined and crash paths. AC5 (was AC3) runs one clean, one reported and one errored unit and asserts the examined figure handed to _record_revert_yield is exactly 1, killing an error unit falling through to examined; with an examined unit beside the set-aside ones it no longer duplicates RevertCheckLaneTests.test_a_reported_unit_is_not_counted_as_examined. Judged 3 points, up from 2. |
