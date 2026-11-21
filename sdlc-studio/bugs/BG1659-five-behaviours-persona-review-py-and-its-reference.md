# BG1659: Five behaviours persona_review.py and its reference page state have no test: a mutant of each passes test_persona_standard.py

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_persona_standard.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T08:39:53Z

## Summary

US1052's qa seat (verdict sdlc-studio/reviews/verdicts/US1052/fdf0d5d75ae1-7505788d.txt, RUN-01M7VNR0) found five behaviours that run correctly but that no test pins: the exit 2 for a --card naming no card (`persona_review.py`:224, stated in reference-scripts-review.md; without the guard a mistyped --card prints blocks=0 and exits 0), seat cards inside the Evidence rule (`persona_review.py`:191), and three more the verdict lists. `test_persona_standard.py` is the only module importing `persona_review`, so a later edit could revert any of them with the suite green.

US1053's qa seat (verdict `sdlc-studio/reviews/verdicts/US1053/d36270849ea5-a6834056.txt`) adds one: the confinement case for `persona_review.py record` (`test_confinement.py`:332-336) proves file-level confinement only, so a mutant making `persona_gen.accept` append a line to the card body passes it. `test_persona_review_record.py`:215 holds that guarantee today, so this is a precision gap, not a hole.

## Steps to Reproduce

Apply the verdict's mutants one at a time in a copy and run tests/`test_persona_standard.py`: each stays green.

## Proposed Fix

Add one test per behaviour that fails on its mutant.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1052's qa seat (verdict sdlc-studio/reviews/verdicts/US1052/fdf0d5d75ae1-7505788d.txt, RUN-01M7VNR0) found five behaviours that run correctly but that no...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Apply the verdict's mutants one at a time in a copy and run tests/`test_persona_standard.py`: each stays green.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add one test per behaviour that fails on its mutant.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. persona_review exit codes and rules are correct; five mutants survive for want of tests. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
