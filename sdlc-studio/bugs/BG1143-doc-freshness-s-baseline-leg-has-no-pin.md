# BG1143: doc_freshness's baseline leg has no pin for checking every Coverage line, nor for skipping the revision history

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, US1098 APPROVE round 2 by qa-seat-US1098-r1 (brief 66ed763beade).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T00:29:12Z

## Summary

qa-seat-US1098-r1's round-2 APPROVE of US1098 (2026-11-01) found two baseline-leg behaviours that are correct at HEAD but pinned by no test, introduced by US1098 (bdccb0e2). M16 checks only the first `Coverage:` baseline (`list(_BASELINE_CLAIM.finditer(body))[:1]` at `doc_freshness.py`:207). M17 reads baselines from the whole file, revision history included (`finditer(_read(path))` in place of `finditer(body)`). Both survive all 28 tests in `test_doc_freshness.py.` The count leg has the equivalent pins (`test_every_occurrence_is_checked_not_the_first` and the revision-history tests); the baseline leg has its own finditer and none.

## Steps to Reproduce

1. In a throwaway worktree apply M16, then M17, to `doc_freshness.py.`
2. Run `test_doc_freshness.py`: green under each.
3. Through the CLI: a PRD with v3.2.1 then v3.1.0 gives 1 finding at HEAD and 0 under M16; a PRD whose Revision History table holds `Coverage: v2.0.0` gives 0 at HEAD and 1 under M17.

## Proposed Fix

Add two baseline-leg tests that mirror the count leg's: a second stale Coverage line is reported, and a Coverage line inside the revision history is not.

## Acceptance Criteria

- [ ] **AC1** A second, stale Coverage baseline in the same document is reported, so a first-only check fails the test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py
- [ ] **AC2** A Coverage baseline inside the document's revision history is not reported, so a whole-file read fails the test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py

## Impact

Low: the code is right today. Two docstring promises ('every baseline doc currently states', 'one record per occurrence') rest on no test for the baseline leg.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
