# BG1222: The hand-copied-list census runs only at the push gate and matches any three quoted .py names, fixture names included

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_test_census.py, changelog.d/BG1222.md
> **Evidence:** BG1221 round-1 verdict, scratchpad run5/BG1221-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T20:46:55Z

## Summary

2026-11-04, BG1221's review (pre-existing). tools/tests/`test_test_census.py` declares no test-census-subject for the files it scans, so a commit to a test file never selects it and it refuses only at the push gate, as BG1220's and BG1221's cases both showed. Its pattern at line 726 matches any three quoted lower-case `.py` names, so a fixture list of three made-up file names trips it the same as a hand-copied list of shipped scripts.

## Steps to Reproduce

1. Add `["a.py", "b.py", "c.py"]` to any scripts test and commit: the hook passes.
2. Push: the gate refuses on HandCopiedMirrorTests.

## Proposed Fix

Match only names of shipped scripts (from the owner hookutil reads), and give the census a test-census-subject so a commit to a test file selects it.

## Acceptance Criteria

- [ ] **AC1** A fixture list of three made-up .py names is not flagged, and a hand-copied list of shipped scripts still is.
  - **Verify:** pytest tools/tests/test_test_census.py::HandCopiedMirrorTests

## Impact

Every fixture list of three file names fails the push gate after its commit passed.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Census test matches any three quoted .py names and runs only at the push gate; it is correct on the real tree, a test-precision gap. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
