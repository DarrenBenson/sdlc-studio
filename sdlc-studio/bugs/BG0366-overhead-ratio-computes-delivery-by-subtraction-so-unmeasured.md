# BG0366: _overhead_ratio computes delivery by subtraction, so unmeasured overhead is reported as delivery

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; predicates mutation-killed)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0523 reports delivery time against overhead as a ratio and US0524 requires an unmeasured component to be reported as unmeasured rather than as zero. The implementation derives delivery as total minus measured overhead, which does the opposite: every minute of overhead the instrument failed to attribute is silently credited to delivery, and the ratio flatters the loop exactly in proportion to how poorly it is measured. The two stories in the same batch contradict each other.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review by reading the ratio's derivation. With one overhead component unrecorded, the reported delivery share rises and no unmeasured marker is emitted, because the subtraction cannot distinguish an absent measurement from a zero one.

## Proposed Fix

Measure delivery directly rather than by residue, and report the unattributed remainder as its own third term. A ratio whose components do not sum to the total is the honest output; a ratio that always sums perfectly is the tell that a residue is being laundered.

## Acceptance Criteria

### AC1: The overhead line states that delivery is derived by SUBTRACTION, so unattributed time is counted as delivery

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadRatioTests::test_an_unmeasured_component_is_not_credited_to_delivery
- **Verified:** yes (2026-09-27)

### AC2: A recorded round duration feeds the term rather than leaving it unmeasured

- **Verify:** manual - retired by BG0783: no record the run writes times a review since US0918 deleted the close-review round's writer, so the overhead's review component reads NOT CAPTURED and the round-duration read is deleted
- **Verified:** manual (2026-09-27) - retired, superseded by BG0783

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery. |
| 2026-09-27 | BG0783 | AC1 re-pointed at OverheadRatioTests' delivery-ceiling test, which pins the subtraction it states; AC2 retired in the D0259 pattern: no record the run writes times a review since US0918 deleted the close-review round's writer, so the overhead's review component reads NOT CAPTURED and the round-duration read is deleted |
