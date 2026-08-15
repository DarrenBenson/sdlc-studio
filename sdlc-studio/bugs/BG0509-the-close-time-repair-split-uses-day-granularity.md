# BG0509: the close-time-repair split uses day granularity and a global override map, so a same-day terminal is excused and an override never expires

> **Status:** Fixed
> **Verification depth:** functional (both halves established by driving close_time_repairs and close_repair_overrides against a real workspace: same-day unaccounted without a record, a close-time repair with one, a later day untouched, and an override invisible to a later close; the first two CLI reproductions were themselves wrong and are recorded in the Resolution; mutation: 3 declared mutants, all KILLED, restore byte-exact)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Two residual defects in US0617/US0618, both reported by the independent review of EP0204 and both pre-existing at the declared base ref. First: `close_time_repairs` compares dates at DAY granularity with a >= test, so a unit that reached terminal EARLIER on the same day as the retro is classified a close-time repair and released from the exit code - contradicting US0617's own definition of after. Second: `close_repair_overrides` scans every retro into one global map with no scoping to a run, so a recorded override forgives that unit permanently in all later runs rather than for the close that needed it.

## Steps to Reproduce

Date a retro 2026-02-01 with a Batch naming BG0001, record BG0005 terminal on 2026-02-01, and run `close_owed` detect: it exits 0 where the same fixture before US0617 exited 1. For the override half, record a Close-repair-override in one retro and observe it still forgiving the same unit in a later run's detect.

## Proposed Fix

Carry a timestamp rather than a day for the terminal record, or compare strictly greater when the dates are equal and the retro's own commit is later. Scope the override to the run that recorded it, keyed on the retro or run id, so an exception expires with the close it was granted for.

## Acceptance Criteria

- [x] **AC1** Given a unit terminal on the SAME DAY as the retro with nothing recorded, when the split runs, then it is unaccounted rather than a close-time repair - the two sides carry only days, so same-day is unknowable and may not be excused on an inference.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py -k same_day_terminal_is_not_excused
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given the same day with a reasoned `Close-repair-override` in that retro, then it IS a close-time repair - a genuine ceremony-time fix survives, moved from inferred to stated.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py -k same_day_terminal_IS_excused_when
  - **Verified:** yes (2026-08-14)
- [x] **AC3** Given an override recorded in one retro, when a LATER close is judged, then it does not forgive that unit - a decision about one close is not a standing exemption.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py -k override_does_not_forgive_a_unit_in_every_later
  - **Verified:** yes (2026-08-14)
- [x] **AC4** Given a unit terminal on a later day than the retro, when the split runs, then it is still a close-time repair - the ordinary case is untouched.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py -k later_terminal_is_still_a_close_time_repair
  - **Verified:** yes (2026-08-14)

## Impact

The first releases a unit from the ledger's exit code on the strength of a same-day coincidence, which is the direction that under-reports. The second makes an exception permanent, which is how a deliberate one-off becomes routine - the exact thing US0618 states it exists to prevent.

## Resolution

Neither side of the comparison carries a time. The retro has `> **Date:** YYYY-MM-DD`; the terminal date is parsed out of an actuals FILENAME. So a unit terminal at 09:00 and a retro written at 14:00 on the same date are indistinguishable from the reverse, and no finer comparison was available to invent.

`>=` resolved that ambiguity in the excusing direction. The repair resolves it the other way - strictly later, UNLESS the retro says otherwise. That keeps the genuine case, which is usually same-day: a close-time repair found during the ceremony is now recorded through the `Close-repair-override` the ceremony already has, so the excusal is STATED rather than inferred. An unanswered question does not get to excuse anything.

The override half is the same disease at a different scale: the map was built from every retro ever written, so one override forgave its unit permanently in all later runs. It is now scoped to the close being judged.

Verification note, recorded because it nearly went the other way: the first CLI reproduction of this was wrong twice - a mis-keyed baseline that made both arms hit the corrupt-baseline path, then an override line in a format the parser does not accept. Both runs looked like evidence and were not. The behaviour was established by driving `close_time_repairs` and `close_repair_overrides` directly against a real workspace, and the fixture is now a test.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in close_owed.py `close_time_repairs`, restore the `>=` day comparison | Given a unit terminal on the SAME DAY as the retro with nothing recorded, when the split runs, then it is unaccounted rather than a close-time repair - the two sides carry only days, so same-day is unknowable and may not be excused on an inference. |
| AC2 | in close_owed.py `close_time_repairs`, ignore the stated same-day override | Given the same day with a reasoned `Close-repair-override` in that retro, then it IS a close-time repair - a genuine ceremony-time fix survives, moved from inferred to stated. |
| AC3 | in close_owed.py `close_repair_overrides`, drop the `on_or_after` scoping filter | Given an override recorded in one retro, when a LATER close is judged, then it does not forgive that unit - a decision about one close is not a standing exemption. |
| AC4 | in close_owed.py `close_time_repairs`, require same-day for a repair so a later day is unaccounted | Given a unit terminal on a later day than the retro, when the split runs, then it is still a close-time repair - the ordinary case is untouched. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
