# BG0657: The scheduled corpus lane is red at 23 against a baseline of 20, and the baseline records only a COUNT, so no reader can tell which three are new

> **Status:** Open
> **Severity:** Medium
> **Points:** 8
> **Verification depth:** functional (authored at plan time; the derived half is written by `verify_ac.py depth --write` at delivery)
> **Affects:** tools/verify-corpus.sh, tools/verify-corpus-baseline.txt, tools/tests/test_verify_corpus.py, .claude/skills/sdlc-studio/scripts/gate.py
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

- [ ] **AC1** Given `gate.py` reporting red acceptance criteria, when its identity emission is driven DIRECTLY rather than through the lane, then the FULL list is available whatever `_MAX_NAMED` does to the human line. Driving it directly is the criterion, not a detail: every existing node in this module runs the lane against a stub printing a hand-written gate string, so a mutant inside `gate.py` reddens nothing there and would be reported as survived. The line elides after ten and appends a count of the rest, which is why this bug's own Summary lists exactly ten; a lane parsing that line can never see more, so the identities have to be obtainable before they can be recorded
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_the_full_red_identity_list_survives_the_elision
  - **Verified:** no
- [ ] **AC2** Given the corpus baseline, when it is read, then EACH metric - `red-criteria` and `dead-stamps` - carries the identities behind its count, and the count agrees with the length of that list. The parse takes the red clause alone and not the 67-row exclusion ledger printed after it, which is the same discriminator the count parse already needed
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_each_metric_records_identities_that_agree_with_its_count
  - **Verified:** no
- [ ] **AC3** Given a run whose red set has GROWN, when the lane reports, then it names the new ids and the ones that went green, and exits non-zero
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_the_lane_names_what_rose_and_what_went_green
  - **Verified:** no
- [ ] **AC4** Given a run whose red set changed by an equal-sized SWAP - one criterion repaired and another introduced in the same window - when the lane runs, then it exits NON-ZERO and names both sides. Today the counts match, the lane exits 0 and the swap is silent: this is the case the count alone cannot carry, and the reason the identities are worth recording at all
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_an_equal_sized_swap_is_not_silent
  - **Verified:** no
- [ ] **AC5** Given a baseline identity that no longer exists - a unit deleted, a criterion renumbered - when the lane runs, then it SAYS so rather than counting the absence as a repair, which would let the number fall for a reason nobody chose
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_a_vanished_identity_is_named_rather_than_counted_as_repaired
  - **Verified:** no
- [ ] **AC6** Given the REAL `gate.py` emitter run once over this tree, when its output is parsed by the lane's own parser, then the parse succeeds and the committed baseline still names both metrics in the shape the existing pinning test reads. This is the anchor the stubbed nodes cannot supply - a parser written against a hand-written fixture agrees with a string nobody produces - and it is the compatibility the format change must not break
  - **Verify:** pytest tools/tests/test_verify_corpus.py::BaselineIdentityTests::test_an_unchanged_tree_still_passes_and_the_format_still_parses
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/gate.py, wrap the machine-readable identity payload in a call to `_elide` | Given `gate.py` reporting red acceptance criteria, when its identity emission is driven DIRECTLY rather than through the lane, then the FULL list is available whatever `_MAX_NAMED` does to the human line. Driving it directly is the criterion, not a detail: every existing node in this module runs the lane against a stub printing a hand-written gate string, so a mutant inside `gate.py` reddens nothing there and would be reported as survived. The line elides after ten and appends a count of the rest, which is why this bug's own Summary lists exactly ten; a lane parsing that line can never see more, so the identities have to be obtainable before they can be recorded |
| AC2 | in tools/verify-corpus.sh, remove the length comparison between a metric's count field and its identity field | Given the corpus baseline, when it is read, then EACH metric - `red-criteria` and `dead-stamps` - carries the identities behind its count, and the count agrees with the length of that list. The parse takes the red clause alone and not the 67-row exclusion ledger printed after it, which is the same discriminator the count parse already needed |
| AC2 | in tools/verify-corpus.sh, drop the discriminator that stops the capture at the clause boundary | Given the corpus baseline, when it is read, then EACH metric - `red-criteria` and `dead-stamps` - carries the identities behind its count, and the count agrees with the length of that list. The parse takes the red clause alone and not the 67-row exclusion ledger printed after it, which is the same discriminator the count parse already needed |
| AC3 | in tools/verify-corpus.sh, delete the two set-difference computations, leaving the numeric comparison | Given a run whose red set has GROWN, when the lane reports, then it names the new ids and the ones that went green, and exits non-zero |
| AC4 | in tools/verify-corpus.sh, insert an early `exit 0` as soon as the two counts are equal | Given a run whose red set changed by an equal-sized SWAP - one criterion repaired and another introduced in the same window - when the lane runs, then it exits NON-ZERO and names both sides. Today the counts match, the lane exits 0 and the swap is silent: this is the case the count alone cannot carry, and the reason the identities are worth recording at all |
| AC5 | in tools/verify-corpus.sh, delete the existence test on each baseline identity, so an absent one falls into the repaired set | Given a baseline identity that no longer exists - a unit deleted, a criterion renumbered - when the lane runs, then it SAYS so rather than counting the absence as a repair, which would let the number fall for a reason nobody chose |
| AC6 | in tools/verify-corpus-baseline.txt, rename the two metric keys so the committed parse no longer matches them | Given the REAL `gate.py` emitter run once over this tree, when its output is parsed by the lane's own parser, then the parse succeeds and the committed baseline still names both metrics in the shape the existing pinning test reads. This is the anchor the stubbed nodes cannot supply - a parser written against a hand-written fixture agrees with a string nobody produces - and it is the compatibility the format change must not break |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-08 | Claude Fable 5.1 | Filed |
