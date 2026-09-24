# BG0760: US0905 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Carried work:** the round-2 patch is kept at sdlc-studio/.local/US0905-carried-r2.patch (tests) and US0905-carried-r2-retire.patch (US0268 AC4 and BG0420 AC2 retirements), both complete against 25cbd375. Remaining fix: draw the AC2 test's pin-scan controls and the AC1 helpers' anchor from the keys `--list` prints rather than from named lanes, so dropping any one lane leaves the suite green; then amend US0372 AC2 in the D0259 pattern
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_lean_commit_lanes.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_test_census.py, changelog.d/US0905.md, sdlc-studio/stories/US0268-order-the-pre-commit-lanes-cheapest-first-so.md, sdlc-studio/bugs/BG0420-test-fixtures-mirror-real-lists-by-hand-so.md, tools/tests/test_message_first_gate.py
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0905 was rejected at round 2, the review cap, by qa-rev-US0905, so it was carried as a known issue rather than reviewed again. The findings still open: [new] MOVED: the AC2 anti-pin test hard-codes 11 lane names in its controls and the AC1 helpers anchor on links, so dropping budgets or versions fails only the cap's own test and the one-lane-pin claim stays false [LC-002]; [new] non-blocking: US0372 AC2 reads every lane still runs but its now-derived test passes with a lane deleted [LC-002]; [new] non-blocking: narrowing the pin scan to tools/tests survives [LC-002]

## Steps to Reproduce

1. Read the round 2 REJECT of US0905 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0905 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0905 was rejected at round 2, the review cap, by qa-rev-US0905, so it was carried as a known issue rather than reviewed again.
- [ ] **AC2** The proposed fix lands, pinned by a test: Fix each finding above, then deliver US0905 again in a later run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
