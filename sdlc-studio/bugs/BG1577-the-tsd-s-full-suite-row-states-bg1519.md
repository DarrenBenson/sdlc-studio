# BG1577: The TSD's full-suite row states BG1519's count floor but not that a commit whose selection holds only push-deferred tests is exempt

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/tsd.md, tools/tests/test_lean_gate_docs.py, changelog.d/BG1577.md
> **Evidence:** BG1519 QA verdict, sdlc-studio/reviews/verdicts/BG1519/b4860a569b60-148ea286.txt
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T02:08:13Z

## Summary

BG1519 (run sixteen) refuses a run in which no test ran, except a commit whose selection holds only boundary-only tests deferred to the push. The TSD's full-suite row states the floor and omits the exemption, so a reader expects such a commit to be refused. Reported non-blocking by the QA review of BG1519.

## Steps to Reproduce

Read the full-suite row of sdlc-studio/tsd.md, then commit a change whose selection is only a boundary-only test: it passes.

## Proposed Fix

Add the exemption to the row and pin it in the doc test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1519 (run sixteen) refuses a run in which no test ran, except a commit whose selection holds only boundary-only tests deferred to the push.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read the full-suite row of sdlc-studio/tsd.md, then commit a change whose selection is only a boundary-only test: it passes.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add the exemption to the row and pin it in the doc test.

## Impact

The test strategy misstates when the floor refuses.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. The repo TSD full-suite row omits a boundary-only exemption; it concerns this repository's commit gate only and is not shipped to users. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
