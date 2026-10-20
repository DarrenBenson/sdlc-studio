# BG1099: US1084's TSD rewording broke US0253 AC3's verifier, which greps for the test-noise leg running in CI

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/tsd.md, changelog.d/BG1099.md
> **Evidence:** lint.yml run 39322298831 (2026-10-19, at 8653d0c9), corpus-verify: 'red-criteria: 2, baseline 0 - NEW: US0253::AC3 US0940::AC1'. `git log -S'is held in CI'` names 69c8c210.
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-20T07:04:46Z

## Summary

US1084's round-1 repair (69c8c210) reworded the TSD's noise-ratchet sentence from 'The `test-noise` leg **runs in CI**' to '**is held in CI**'. US0253 AC3 verifies with `grep "test-noise.*runs in CI" sdlc-studio/tsd.md`, which now matches nothing, so the criterion, on a story at Done, reads red. No test suite runs a grep Verify line, so the push gate passed it, and the weekly corpus-verify job caught it on dispatched run 39322298831.

## Steps to Reproduce

`grep "test-noise.*runs in CI" sdlc-studio/tsd.md` -> no output, exit 1. Dispatched run 39322298831: `NEW: US0253::AC3 US0940::AC1`.

## Proposed Fix

Word the sentence so it still says the leg runs in CI, on the line that names it, keeping US1084's correction of where it is held.

## Acceptance Criteria

- [ ] **AC1** US0253 AC3's own verifier passes against the TSD
  - **Verify:** shell grep -q "test-noise.*runs in CI" sdlc-studio/tsd.md
  - **Verified:** yes (2026-10-20)

## Impact

A Done story's criterion reads red, and the weekly lane fails until it is fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | Claude Opus 5.5 | Filed |
