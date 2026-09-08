# BG0657: The scheduled corpus lane is red at 23 against a baseline of 20, and the baseline records only a COUNT, so no reader can tell which three are new

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional (authored at plan time; the derived half is written by `verify_ac.py depth --write` at delivery)
> **Affects:** tools/verify-corpus.sh, tools/verify-corpus-baseline.txt, tools/tests/test_verify_corpus.py
> **Evidence:** Run on 2026-09-08: dead-stamps 3 of 3 baseline OK, red-criteria 23 against baseline 20, gate wall-clock 1687s.
> **Created:** 2026-09-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5.1; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`tools/verify-corpus.sh full` reports `red-criteria: 23, baseline 20 - 3 NEW one(s)` and instructs the reader to find and fix them rather than raise the baseline. Nothing lets them. `tools/verify-corpus-baseline.txt` carries a bare number per metric, so identifying WHICH three requires re-running the same 28-minute lane against the baseline commit and diffing two lists by hand. Measured on this tree: the release gate names red criteria across 8 units already at Done (10 criteria: US0021 AC1, US0040 AC3, US0042 AC2, US0047 AC1, US0052 AC4, US0063 AC1 and AC2, US0070 AC1 and AC2, US0080 AC2), plus 68 on Ready stories and 55 on Blocked ones whose features are unbuilt by construction. Dead stamps are at baseline. The lane is a v5.1 bar clause and it cannot currently be discharged by anyone who did not run it before and after.

## Steps to Reproduce

1. `bash tools/verify-corpus.sh full` - about 30 minutes.
2. Read `corpus-verify FAILED: red-criteria: 23, baseline 20 - 3 NEW one(s)`.
3. Read `tools/verify-corpus-baseline.txt`: it holds `red-criteria|20|<prose>` and no identities.
4. Try to name the three. There is no recorded list to diff against.

## Proposed Fix

Record the IDENTITIES beside the count, so the lane can name what rose rather than only that something did, and report the new ones by id. Keep the count as the gate.

## Acceptance Criteria

- [ ] **AC1** Given the corpus baseline, when it is read, then it carries the IDENTITIES behind each count - the unit and criterion of every tolerated red one - so a rise can be named rather than only detected. The count stays the gate; the list is what makes the lane's own instruction, find it and fix it, possible for a reader who did not run it before.
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_the_baseline_records_the_identities_behind_its_count
  - **Verified:** no
- [ ] **AC2** Given a run whose red set has grown, when the lane reports, then it NAMES the new ids and the ones that went green, so a rise and a swap of equal size are told apart - today a red criterion repaired and another introduced in the same window reports as no change at all.
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_the_lane_names_what_rose_and_what_went_green
  - **Verified:** no
- [ ] **AC3** Given a baseline whose recorded identities no longer exist - a unit deleted or a criterion renumbered - when the lane runs, then it says so rather than counting the absence as a repair, which would let the number fall for a reason nobody chose.
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_a_vanished_identity_is_named_rather_than_counted_as_repaired
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/verify-corpus.sh, drop the identity list from the baseline write so only the count is recorded | Given the corpus baseline, when it is read, then it carries the IDENTITIES behind each count - the unit and criterion of every tolerated red one - so a rise can be named rather than only detected. The count stays the gate; the list is what makes the lane's own instruction, find it and fix it, possible for a reader who did not run it before. |
| AC2 | in tools/verify-corpus.sh, compare the counts alone so an equal-sized swap reports no change | Given a run whose red set has grown, when the lane reports, then it NAMES the new ids and the ones that went green, so a rise and a swap of equal size are told apart - today a red criterion repaired and another introduced in the same window reports as no change at all. |
| AC3 | in tools/verify-corpus.sh, change a missing recorded identity to count as repaired | Given a baseline whose recorded identities no longer exist - a unit deleted or a criterion renumbered - when the lane runs, then it says so rather than counting the absence as a repair, which would let the number fall for a reason nobody chose. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-08 | Claude Fable 5.1 | Filed |
