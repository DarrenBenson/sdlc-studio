# BG1464: retro.py's own-finding check matches a review word anywhere in Evidence and two of its guards have no test

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py, changelog.d/BG1464.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** QA seat's round-2 review of US1064, run thirteen (sdlc-studio/reviews/verdicts/US1064/5f18b00eea1b-9a8fc9a5.txt).
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:17:54Z

## Summary

In US1064's seat record, `_own_finding` decides whether a later bug was the approving review's own finding. `_REVIEW_RE` (retro.py near line 1553) matches reviewed or reviewer anywhere in the bug's Evidence, and nothing ties the approving row's finding to the bug: Evidence of 'production log after US0001 was reviewed', over an APPROVE carrying an unrelated finding, reads as approved over its own finding, so a real miss goes uncharged. Separately, removing the review-word check or the unit-in-Evidence check (near line 1620) still passes all 13 tests in `test_retro_seat_misses.py` and `test_retro_seat_evidence.py.`

## Steps to Reproduce

1. File an Escaped-via bug whose Evidence says the unit 'was reviewed' over an APPROVE with an unrelated finding.
2. Run retro.py seats: the bug reads as the approval's own finding and is not charged.
3. Mutate away either guard in `_own_finding`: the tests still pass.

## Proposed Fix

Treat a bug as the approval's own finding only when the approving row's finding text names the bug's defect (its file:line or id), and add a test that kills each guard's removal.

## Acceptance Criteria

- [ ] **AC1** Given an Escaped-via bug whose Evidence reads 'production log after US0001 was reviewed', over an APPROVE carrying a finding that names neither the bug nor its defect, when `retro.py seats` runs, then the bug is charged to the approving seat as missed. Fails on: a review word anywhere in Evidence reading as approved over its own finding.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_review_word_in_evidence_over_an_unrelated_finding_is_a_miss
- [ ] **AC2** Given a bug whose Evidence names the unit's review and the approving row's finding names the bug's defect (its file and line, or its id), when `retro.py seats` runs, then the bug is listed as approved over the seat's own finding, with that finding's text. Fails on: the tightened rule charging a seat for a defect it raised and passed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_finding_naming_the_bugs_defect_reads_approved_over_its_own_finding
- [ ] **AC3** Given a bug whose Evidence names a review but not the charged unit, and one whose Evidence names the unit but no review, when `retro.py seats` runs, then each is charged as missed. Fails on: either guard of `_own_finding` removed with every test still green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_evidence_missing_the_unit_or_the_review_is_a_miss

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. An own-finding check and two untested guards.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
