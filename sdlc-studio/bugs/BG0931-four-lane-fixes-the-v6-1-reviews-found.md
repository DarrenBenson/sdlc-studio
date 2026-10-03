# BG0931: Four lane fixes the v6.1 reviews found unpinned: a split forecast, a reopened re-close, the newest transcript and a partial run

> **Status:** In Progress
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_lane1_pins.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/transition.py, changelog.d/BG0931.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T13:08:00Z

## Summary

The v6.1 lane 1 reviews approved BG0924, BG0926, BG0927 and BG0930 but each found a behaviour its tests do not hold: BG0924's reason when one unit has the forecast and another the minutes; BG0926's guard on a run reopened then re-closed (mutants reopens[0] and 'return not reopens' at `run_state.py` ~1582 survive and would let a late return invalidate a page); BG0927's choice of the newest transcript (an oldest-first mutant survives); BG0930's skip for a 'partial' run, the outcome of the web run that raised it.

## Steps to Reproduce

Apply each named mutant in a scratch copy; the unit's own tests still pass.

## Proposed Fix

Add the four pins; no behaviour change unless a pin exposes a defect.

## Acceptance Criteria

- [ ] **AC1** Given a run where one unit carries the forecast and a different unit the minutes, when the page is built, then the Minutes reason names the missing pair. Fails on: a reason chosen from no forecast anywhere
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_lane1_pins.py::V61Lane1PinsTests::test_a_split_forecast_names_the_missing_pair
- [ ] **AC2** Given a run reopened after its page was filed and then re-closed, when lane return --tokens is run before the sign, then nothing is recorded and the page checks VALID. Fails on: the reopens[0] and 'return not reopens' mutants
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_lane1_pins.py::V61Lane1PinsTests::test_a_reopened_re_close_records_no_late_total
- [ ] **AC3** Given a matching project folder with an older and a newer transcript, when the transcript is resolved, then the newer one is read. Fails on: an oldest-first pick
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_lane1_pins.py::V61Lane1PinsTests::test_the_newest_transcript_is_read
- [ ] **AC4** Given a signed run whose outcome is partial, when transition.py set moves a unit, then no APPETITE SPENT warning is printed. Fails on: a skip for goal-reached only
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_lane1_pins.py::V61Lane1PinsTests::test_a_partial_run_spends_no_appetite

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
