# BG0495: the velocity row understates twice - it counts only accepted points, over a wall-clock with no idle deducted

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, sdlc-studio/retros/VELOCITY.md
> **Severity:** Medium
> **Points:** 5
> **Verification depth:** functional

## Summary

RETRO0089 recorded 4.96 points/elapsed-hour for RUN-01KYZKY5 and the operator immediately queried it: the sprint was planned at 152 points and ran about 15 hours. Both halves of the ratio are wrong, and both in the same direction.

NUMERATOR. The row counts 76 points, being the units in a TERMINAL status. The batch holds 148 points; 72 of those are delivered, committed, working code sitting at Ready because the review rejected it. So the figure measures ACCEPTED work while its label says only 'points', and a run that wrote 148 points and had 72 rejected is reported as a run that was slow rather than one that was rejected. Those are different facts and only one of them is a velocity.

DENOMINATOR. `sprint stop` reported '15.312h wall-clock less 0.0h idle INSIDE it, from 0 recorded gap(s)'. This was an interactive session containing six full suite runs of roughly nine minutes each and several long periods with nobody at the keyboard. Zero recorded idle across fifteen hours is not credible, so the elapsed figure is closer to a calendar span than to working time.

Combined, the two push the ratio far below the operator's own felt heuristic of roughly three minutes per point, which is what made it visible.

## Steps to Reproduce

1. Read the Velocity line in RETRO0089: 4.96 points/elapsed-hour, 76 points over 15.312h.
2. Sum the batch's points by terminal status: 76 terminal across 25 units, 72 non-terminal across 19, 148 total.
3. Read the `sprint stop` output: 0.0h idle from 0 recorded gaps, over a 15.3h interactive run.

## Proposed Fix

Report the two numerators separately and label them: points DELIVERED (written, committed, gate-green) and points ACCEPTED (terminal after review). A run that delivers 148 and has 72 rejected should show both, since the gap is the most interesting number on the row. For the denominator, either record idle gaps for an interactive run or state plainly that the elapsed figure is a calendar span with no idle deduction - an unqualified 'working hours' that is really wall-clock is a claim the tooling cannot support.

## Acceptance Criteria

- [x] **Two numerators, separately labelled.** The velocity row reports points WRITTEN (shipped and reviewed) beside points ACCEPTED (terminal), and names the units in the gap. Status alone cannot separate them - a rejected story returns to `Ready`, indistinguishable from one nobody started - so the test is a recorded delivery verdict, which is evidence the diff exists. *Mutant:* count only terminal work - a sprint that wrote 8 and had 5 rejected reads as one that delivered 3. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityRowTests::test_delivered_and_accepted_points_are_reported_separately
- [x] **A unit nobody reviewed is not counted as written.** The negative control, without which `written` is `planned` renamed. *Mutant:* count every non-terminal unit - an unstarted story inflates the output figure, over-claiming in exactly the direction this bug exists to stop. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityRowTests::test_a_unit_nobody_reviewed_is_not_counted_as_written
- [x] **A denominator with no recorded idle says so.** The gap COUNT travels with the elapsed figure, and a run-state span with zero recorded gaps is labelled a CALENDAR SPAN with no idle deducted. Zero gaps is no measurement of idle, not an absence of it. *Mutant:* keep the unqualified label - the tooling makes a claim it cannot support. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityRowTests::test_a_zero_idle_span_is_labelled_a_calendar_span
- [x] **A run that DID measure its idle is not told its figure is unqualified.** The positive control: a qualifier printed unconditionally distinguishes nothing. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityRowTests::test_a_recorded_gap_is_not_labelled_a_calendar_span
- [x] **A row with no recorded wall-clock reports UNMEASURED, not a ratio.** This behaviour PREDATES the bug and is pinned rather than built - no VELOCITY.md row since RETRO0027 carries a wall-clock, so absence is the common case and must stay visible. *Mutant:* divide by a defaulted elapsed - every unmeasured run acquires a velocity nobody measured. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityRowTests::test_a_row_without_wall_clock_reports_unmeasured
- [x] **The delivery figure is marked an upper bound, as the ratio beside it is marked a lower one.** RESTATED from the filed wording, which asked for the delivery share to be REFUSED whenever a component was unmeasured. Reading the code first showed the premise was half stale: `_overhead_ratio` already carries a `bound` and already prints "at least" on the ratio and names the excluded components. What it did not do was qualify the delivery minutes, so one sentence carried a qualified claim and an unqualified one about the same subtraction. Refusing the figure outright would have destroyed a useful lower bound to fix a labelling defect. *Mutant:* hard-code either qualifier - the two stop coming from one decision. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadRatioTests::test_an_unmeasured_component_is_not_credited_to_delivery
- [x] **The two qualifiers are derived from one `bound`, not written beside each other.** *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadRatioTests::test_the_two_qualifiers_come_from_one_decision
- [x] **The existing rows in VELOCITY.md are not retrospectively rewritten.** The Written column is ADDED; a row that predates it records no written figure, and that is an absence rather than a claim that nothing was rejected. *Mutant:* recompute the file on write - the before-and-after baseline this sprint is judged on disappears. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityRowTests::test_historical_rows_are_preserved_and_marked
- [x] **The header and the row writer enumerate the same columns.** Found the hard way: VELOCITY.md's schema is written out THREE times - the header string, the writer's f-string and the reader's dict - and nothing made them agree. Adding `Written` to the header alone silently shifted every cell after it in every historical row, so the estimate column read back the actual and the actual read back the ratio. *Mutant:* drop one cell from the writer - the counts differ and this reddens. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::VelocityRowTests::test_the_header_and_the_row_writer_enumerate_the_same_columns

## Impact

VELOCITY.md is what the plans quote, and the estimator memo already warns that velocity is descriptive and never a target. A number that understates by roughly half on the numerator and an unknown amount on the denominator does not just mislead about speed - it hides the actual finding, which is that a fifth of this batch was rejected on review. The first person to act on it would conclude the team is slow rather than that the evidence was weak.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
