# BG1158: The TRD verifier-authority scan misses some story-only rewordings and fails true sentences about a story-only run

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_trd_refresh.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, US1099 APPROVE round 2 by qa-seat-US1099-r1 (brief dd3da56d673b).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T06:06:57Z

## Summary

qa-seat-US1099-r1's round-2 APPROVE of US1099 (2026-11-01) left three limits in tools/tests/`test_lean_trd_refresh.py.` (1) `_GAP` (:53) refuses only not, no, never and n't between the set's name and 'the authority', so 'cannot be the authority' and 'mirrors the authority, X' survive. (2) `_narrower_than` (:115) reads only clauses holding a word `_EXECUTING_RE` (:45) matches, so 'Only a story is gated on its Verify lines.' and '`verify_ac.py` evaluates the Verify lines of a story only.' survive. (3) It over-reaches the other way: it judges which types a clause names, not whether the clause is true, so the true sentences '`verify_ac.py run --id US0001` executes that story's Verify lines.' and '`verify_ac.py` executes the Verify lines of a story (and of a bug).' fail, the second because `_CLAUSE_CUT_RE` (:48) cuts at the parenthesis. Any accurate future sentence about a single-story run must name bugs to pass.

## Steps to Reproduce

1. In a throwaway worktree, put each sentence above into trd.md in turn.
2. Run tools/tests/`test_lean_trd_refresh.py`: the first four pass, and the two true ones fail.

## Proposed Fix

Refuse the set being anything but the authority by reading the verb (or add cannot and a 'mirrors/copies' guard). Widen the execution words to gate/evaluate. Exempt a clause that names one unit run (an id) rather than a type, and do not cut a clause at a parenthesis that continues the type list.

## Acceptance Criteria

- [ ] **AC1** 'cannot be the authority' and 'mirrors the authority' leads fail AC1.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py
- [ ] **AC2** 'is gated on' and 'evaluates' story-only sentences fail AC1.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py
- [ ] **AC3** A true sentence about one story's run, or naming bugs in a parenthesis, passes.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py

## Impact

Two false greens and a false red in a doc check other units must satisfy; the false red pushes authors to reword true sentences.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
