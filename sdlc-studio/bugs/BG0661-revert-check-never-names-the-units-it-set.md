# BG0661: revert-check never names the units it set aside, and once one unit is examined their count vanishes from the lane line too

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
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

- [ ] **AC1** With one unit examined and one test-only unit in the batch, the revert-check lane's line names the test-only unit by id as reported
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckSetAsideUnitsTests::test_a_reported_unit_is_named_beside_an_examined_one
- [ ] **AC2** With one unit examined and one unit the check could not measure, the line names the errored unit by id
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckSetAsideUnitsTests::test_an_errored_unit_is_named_beside_an_examined_one
- [ ] **AC3** A set-aside unit is still excluded from the examined count - the paired control, true today
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckSetAsideUnitsTests::test_a_reported_unit_is_not_counted_examined

## Impact

The lane's promotion from advisory to blocking will be decided on what its boundary output shows. A reader of that line cannot see which units the method set aside rather than judged, so a blind spot the lane already knows about - every test-only unit - reaches nobody until a reviewer rediscovers it by hand, as BG0601 was.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-10 | Claude Opus 5 | Filed |
| 2026-09-10 | Claude Opus 5 | Ruled OPEN for v5.1 on 2026-09-10, under D0186's disclosure half. revert-check is an ADVISORY lane whose yield is still being measured, so a blind spot in it holds nothing back and misleads nobody: the boundary run records what it examined and this bug names, by id, the class it cannot see - a unit whose production change and its evidence live in one file, which is every test-only unit. Two independent seats reached it on BG0601 and a hand check confirmed 11 of 11 green after the revert. Fixing it means deciding what 'production file' means for a unit that only adds tests, which is a design question and not a patch. |
| 2026-09-15 | sdlc-studio | Retitled: was 'revert-check cannot see a unit whose fix and evidence share one file - it reverts the tests with the change and reports green' |
| 2026-09-15 | sprint planning 2026-09-15 | Groomed for the next batch and NARROWED: the filed mechanism (a test-only unit counted as examined and reported green) is refuted by a fixture at HEAD - such a unit is set aside as reported and never counted. Retitled to the residue: set-aside units are never named by id, and their count vanishes once one unit is examined. CR0511 finding #30 is the same defect, folded in here. Real criteria replace the tool-derived one; 3 -> 2 points. |
