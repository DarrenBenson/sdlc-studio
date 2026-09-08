# BG0655: the survivor filer reads a WITHDRAWN row as a live survivor, so a close files a High bug for a mutant the ledger says is dead

> **Status:** Open
> **Mutation-survivor-run:** RUN-01M1YK70
> **Mutation-survivor:** US0818-4124f2e32130f7e4
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-09-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`transition.py` `_survivor_records` selects a ledger row on its verdict alone - `mu.get("verdict") == "survived"` - with no test for the `withdrawn` mark every other reader applies. A row that was recorded survived, withdrawn with a reason and then re-registered killed is therefore read as a live survivor, and the close files a High bug naming a mutant the ledger says is dead.

This artefact is that false positive, kept and retitled rather than deleted: the run's close filed it against US0818 AC2 r4 at `mutation.py:2173`, where the ledger holds the survived row withdrawn and the killed row live. A false High is not harmless - the v5.1 bar is zero open High, so an over-reporting filer holds a release on evidence that does not exist.

## Steps to Reproduce

1. Take a unit whose ledger row was recorded `survived`, withdrawn with a reason, and re-registered `killed` on the same key - US0818 AC2 r4 on `mutation.py` is one on this tree today.
2. Drive that unit to a terminal status: `transition.py set US0818 Done`.
3. Read the bug the transition files: it names the withdrawn row as a surviving mutant, at High severity.
4. Read `_survivor_records` in `transition.py`: it selects on `mu.get("verdict") == "survived"` with no test for the `withdrawn` mark that `gate.py` and four other readers honour.

## Proposed Fix

Add the `withdrawn` test to the row predicate in `_survivor_records`, so a retracted reading is not offered as evidence. The mark is already written by `mutation.py retract` and already honoured everywhere else that reads a row; this is the one reader that does not.

## Acceptance Criteria

- [ ] **AC1** Given a ledger row recorded `survived` and then WITHDRAWN with a reason, when the survivor filer runs for that unit at a terminal transition, then the row is not offered as a survivor and no bug is filed for it - a withdrawal is the ledger's record that the reading was retracted, and every other reader already honours it. The paired control: a row recorded `survived` and NOT withdrawn is still offered, so the filter narrows the selection rather than emptying it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorFilerTests::test_a_withdrawn_row_is_not_offered_as_a_survivor
  - **Verified:** no
- [ ] **AC2** Given a unit whose only surviving row is withdrawn and whose live row for the same key is `killed`, when the unit reaches its terminal status, then the transition writes no `Mutation-survivor-run` bug, and the run's close reports no survivor for that unit - because a filer that over-reports holds a release on evidence the ledger says does not exist.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SurvivorFilerTests::test_no_bug_is_filed_when_the_live_row_for_the_key_is_killed
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, delete the `withdrawn` test from `_survivor_records`'s row predicate so the selection returns to verdict alone | Given a ledger row recorded `survived` and then WITHDRAWN with a reason, when the survivor filer runs for that unit at a terminal transition, then the row is not offered as a survivor and no bug is filed for it - a withdrawal is the ledger's record that the reading was retracted, and every other reader already honours it. The paired control: a row recorded `survived` and NOT withdrawn is still offered, so the filter narrows the selection rather than emptying it. |
| AC2 | in transition.py, replace the row's own `withdrawn` test with a read of the ledger ENTRY's mark, so a withdrawn row inside a live entry is still offered | Given a unit whose only surviving row is withdrawn and whose live row for the same key is `killed`, when the unit reaches its terminal status, then the transition writes no `Mutation-survivor-run` bug, and the run's close reports no survivor for that unit - because a filer that over-reports holds a release on evidence the ledger says does not exist. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-08 | sdlc-studio | Filed |
