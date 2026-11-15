# BG1463: retro.py seats drops an Escaped-via bug silently when its unit's approval names no seat, has only a REJECT, or post-dates the bug

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py, changelog.d/BG1463.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
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

- [ ] **AC1** The behaviour described is corrected: US1064's seat record names an Escaped-via bug as charged to no seat only when its unit has no live ledger row (the uncharged list, retro.py near line 1663).
- [ ] **AC2** The proposed fix lands, pinned by a test: Name every Escaped-via bug in the window that is not charged to a seat in uncharged, with its reason (no seat on the approval, no approval, approval after the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
