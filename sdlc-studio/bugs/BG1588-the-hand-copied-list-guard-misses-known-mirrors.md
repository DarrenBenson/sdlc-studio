# BG1588: The hand-copied-list guard misses _KNOWN_MIRRORS growing and exempts a whole file on one marker, and BG1586's AC2 cannot tell a marker with no reason

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_test_census.py, sdlc-studio/bugs/BG1586-us1313-s-test-lists-the-gate-scripts-by.md, changelog.d/BG1588.md
> **Evidence:** BG1586 QA verdict, run sixteen, 2026-11-18.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T09:13:57Z

## Summary

The QA review of BG1586 (run sixteen, APPROVE) left three non-blocking findings. First, `test_the_known_mirror_set_only_shrinks` reads only names that left the set, so a name added to `_KNOWN_MIRRORS` passes. Second, the HAND-MAINTAINED ON PURPOSE marker exempts the whole file, so a second, real mirror in the same file is never read. Third, BG1586's AC2 Verify greps D0520 anywhere in `test_repo_risk_map.py`, and the module docstring already names it, so a bare marker with no reason would still pass.

## Steps to Reproduce

Read sdlc-studio/reviews/verdicts/BG1586/b03a7365fa1f-237fba1b.txt. Add a name to `_KNOWN_MIRRORS` and run HandCopiedMirrorTests: green. Add a second three-script literal to `test_repo_risk_map.py`: green.

## Proposed Fix

Pin the baseline to a literal size or digest; exempt only the literal next to the marker; tighten BG1586's AC2 to read the reason on the marker's own comment.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The QA review of BG1586 (run sixteen, APPROVE) left three non-blocking findings.
- [ ] **AC2** The proposed fix lands, pinned by a test: Pin the baseline to a literal size or digest; exempt only the literal next to the marker; tighten BG1586's AC2 to read the reason on the marker's own comment.

## Impact

The guard can be widened, or sidestepped inside a declared file, with its tests still green.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. The mirror-guard has three weak spots found at review; no hand-copied list is currently wrong. Tests only. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
