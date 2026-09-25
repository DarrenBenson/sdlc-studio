# BG0760: US0905 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Depends on:** BG0761 - its carried patch applies only after BG0761's (QA grooming)
> **Carried work:** the round-2 patch is kept at sdlc-studio/.local/US0905-carried-r2.patch (tests) and US0905-carried-r2-retire.patch (US0268 AC4 and BG0420 AC2 retirements), both complete against 25cbd375. Remaining fix: draw the AC2 test's pin-scan controls and the AC1 helpers' anchor from the keys `--list` prints rather than from named lanes, so dropping any one lane leaves the suite green; then amend US0372 AC2 in the D0259 pattern
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/tests/test_lean_commit_lanes.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_test_census.py, tools/tests/test_message_first_gate.py, changelog.d/US0905.md, sdlc-studio/stories/US0268-order-the-pre-commit-lanes-cheapest-first-so.md, sdlc-studio/bugs/BG0420-test-fixtures-mirror-real-lists-by-hand-so.md, sdlc-studio/stories/US0372-validate-the-commit-message-rules-ahead-of-the.md
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0905 was rejected at round 2, the review cap, by qa-rev-US0905, so it was carried as a known issue rather than reviewed again. The findings still open: [new] MOVED: the AC2 anti-pin test hard-codes 11 lane names in its controls and the AC1 helpers anchor on links, so dropping budgets or versions fails only the cap's own test and the one-lane-pin claim stays false [LC-002]; [new] non-blocking: US0372 AC2 reads every lane still runs but its now-derived test passes with a lane deleted [LC-002]; [new] non-blocking: narrowing the pin scan to tools/tests survives [LC-002]

The criteria take the blocking finding and the US0372 amendment the carried-work note names; the pin-scan narrowing finding is not re-opened.

## Steps to Reproduce

At 65cdf1ca both patches apply cleanly. With them applied in a scratch copy, the four US0905 modules pass (the one census failure is the copy's missing `node_modules`, and HEAD fails it the same way). Deleting the `budgets` lane from `.githooks/pre-commit` then fails exactly `LaneCapTests::test_the_cap_retires_the_exact_lane_pins`, whose control tuple names `budgets`: the named lanes are a second lane pin.

## Proposed Fix

Apply both carried patches; derive the pin-scan controls and `_add_lanes`/`_drop_lane` anchors from the keys `--list` prints; retire US0372 AC2 in the D0259 pattern, as US0268 AC4 is retired.

## Acceptance Criteria

- [ ] **AC1** Given the carried patches applied and a copy of the hooks with any one lane that `pre-commit --list` prints deleted, when the US0905 cap tests' controls and fixture helpers run against that copy, then each still passes for every lane in turn: the cap count is the only lane pin. Fails on: the carried patch's control tuples that name `budgets` and `versions`, and `_add_lanes` anchored on `run "links"`.
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::LaneCapTests::test_dropping_any_one_listed_lane_leaves_the_cap_tests_green
- [ ] **AC2** Given US0372 AC2 ("every lane that ran before the move still runs"), when its criteria are read with `verify_ac.criteria_blocks`, then its Verify line reads `manual - retired by US0905: ...` and its Verified line says `retired, superseded by US0905`, as US0268 AC4 does, and `verify_ac.py stamps --story US0372` exits 0. Fails on: leaving AC2 stamped against the now-derived inventory test, which passes with a lane deleted.
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::LaneCapTests::test_us0372_ac2_is_retired_rather_than_green_over_a_deleted_lane

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (with both patches applied, deleting the `budgets` lane fails only the cap's own test); criteria are the carried patches plus the remaining fix, each with one Verify line and the wrong fix it fails on; Affects adds US0372; 1 point resized to 2 |
