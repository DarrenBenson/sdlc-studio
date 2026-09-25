# BG0694: tag-check's tests pin the override case, not the blocking predicate, so a later-day close-time repair can be refused again with the suite green

> **Status:** Superseded
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0668-delivery-qa.txt (qa seat); verdicts/BG0668-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. The changelog over-claim the same verdicts raised is already corrected in changelog.d/BG0668.md; the gate and velocity halves are BG0688 and BG0689.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A build that subtracts `close_repair_overrides` from owed passes all three TagCheckReadsTheBlockingPredicateTests, yet still refuses a later-day close-time repair with no override that `close_owed.py` detect exits 0 over, which is the original defect in another shape. The AC1 parenthetical's claim that a later-day fixture would test nothing is false: that fixture refuses at 3f73ab64 and passes at HEAD. The criteria as written are met, so this is a test gap, not a regression. The re-import of `close_owed` at `release_cut.py`:371 is redundant, since the name is already bound at line 340 in the same function scope.

## Steps to Reproduce

1. In a copy, change `release_cut`'s guard to read owed minus `close_repair_overrides` and run TagCheckReadsTheBlockingPredicateTests in `test_release_cut.py` - green. 2. Build a corpus whose only uncovered unit is a close-time repair made on a later day than its close, with no override: `close_owed.py` detect exits 0; under the mutant, `release_cut.py` tag-check refuses.

## Proposed Fix

Add the later-day, no-override fixture beside the override case and assert that tag-check's verdict matches detect's exit on both; drop the redundant import.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: A build that subtracts `close_repair_overrides` from owed passes all three TagCheckReadsTheBlockingPredicateTests, yet still refuses a later-day close-time...
- [ ] **AC2** The proposed fix lands, pinned by a test: Add the later-day, no-override fixture beside the override case and assert that tag-check's verdict matches detect's exit on both; drop the redundant import.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-25 | sdlc | Superseded by US0942: the require-close lane and the tag's close-owed half it describes are retired (US0942 Done) |
