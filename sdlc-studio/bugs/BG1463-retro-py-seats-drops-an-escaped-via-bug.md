# BG1463: retro.py seats drops an Escaped-via bug silently when its unit's approval names no seat, has only a REJECT, or post-dates the bug

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py, changelog.d/BG1463.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/reference-retro.md
> **Evidence:** QA seat's round-2 review of US1064, run thirteen (sdlc-studio/reviews/verdicts/US1064/5f18b00eea1b-9a8fc9a5.txt), probes of all three cases at e8e66f8d.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:17:47Z

## Summary

US1064's seat record names an Escaped-via bug as charged to no seat only when its unit has no live ledger row (the uncharged list, retro.py near line 1663). In three other cases the bug is neither charged nor named, and retro.py seats prints no line for it: the unit's live APPROVE names no seat (1841 of this ledger's 1903 rows), the unit has only a live REJECT, or the unit's only approval is dated after the bug. The docstring (near line 1637) says an Escaped-via unit no review approved is named in uncharged, which is false for the REJECT-only case. An escaped defect that the record never mentions defeats the seat record's purpose for Abena Osei's End goal 4.

## Steps to Reproduce

1. File a bug with Escaped-via naming a unit whose only live verdict is a REJECT (or an APPROVE with no seat, or an APPROVE dated after the bug).
2. Run retro.py seats over a window holding the bug.
3. See no line naming the bug.

## Proposed Fix

Name every Escaped-via bug in the window that is not charged to a seat in uncharged, with its reason (no seat on the approval, no approval, approval after the bug), and correct the docstring.

## Acceptance Criteria

- [ ] **AC1** Given a bug in the retro's window whose Escaped-via unit has only a live REJECT, when `retro.py seats` runs, then the bug is named in uncharged with a reason saying no review approved the unit. Fails on: the bug appearing on no line of the record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_an_escaped_via_unit_with_only_a_reject_is_named_uncharged
- [ ] **AC2** Given a bug whose Escaped-via unit's live APPROVE names no seat, when `retro.py seats` runs, then the bug is named in uncharged with a reason saying the approval names no seat. Fails on: an approval with no seat dropping the bug silently.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_an_escaped_via_unit_whose_approval_names_no_seat_is_named_uncharged
- [ ] **AC3** Given one bug whose Escaped-via unit was approved only after the bug's Created day, and beside it a bug whose unit a seat approved before it, when `retro.py seats` runs, then the first is named in uncharged with a reason saying the approval post-dates the bug, and the second is charged to the seat and absent from uncharged. Fails on: the late approval dropping the bug, or a charged bug also listed as uncharged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_an_approval_after_the_bug_is_named_uncharged_and_a_charged_bug_is_not

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Affects widened to `reference-retro.md`, whose lines 133-134 describe the reasons this fix changes (qa round one) |
