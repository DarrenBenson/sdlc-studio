# BG0740: a gate stood down in prose rather than as a waiver row is invisible to the report's waiver disclosure, which is how the one the operator most needed went unnamed

> **Status:** Open
> **Closes with:** US0926 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py
> **Evidence:** Found by the independent engineering seat reviewing BG0719, 2026-09-22, and confirmed by execution against the real log: 67 accepted waiver rows returned with a 2026-09-30 bound, `D0215 present? True`, `D0214 present? False`. D0214 sits at decisions.md:228 as prose. The defect is in what the vocabulary can express, not in the reader, which is why it is filed separately rather than fixed inside BG0719.
> **Created:** 2026-09-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0719 makes the report of record disclose the waivers in force when it was derived, recognised by the canonical `waiver: <subject>` token `decisions.py` defines. D0214 - the decision that stood `review.line_coverage` down from block to report for RPT0002's seal, and one of the two the bug's own Summary names - is NOT such a row. It is prose, and its own rationale says why: the waiver vocabulary declares no subject for that lane, so `decisions.py waive` could not express it. The disclosure therefore finds D0215 and not D0214, and a re-derived RPT0002 still never names the lane that actually stood down.

## Steps to Reproduce

1. Read D0214 in sdlc-studio/decisions.md - it records a gate standing down and is not a `waiver:` row.
2. Run the report's waiver derivation over a window containing it.
3. It is absent, because no token marks it.

## Proposed Fix

Let a waiver name a lane that declares no subject, so `decisions.py waive` can express the D0214 case and the canonical token covers it. Then backfill D0214 as a waiver row with its original date and rationale, and pin that the disclosure finds both D0214 and D0215 against the real log.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0719 makes the report of record disclose the waivers in force when it was derived, recognised by the canonical `waiver: <subject>` token `decisions.py`...
- [ ] **AC2** The proposed fix lands, pinned by a test: Let a waiver name a lane that declares no subject, so `decisions.py waive` can express the D0214 case and the canonical token covers it.

## Impact

The disclosure is only as complete as the vocabulary that records a stand-down, and the very case that motivated the disclosure cannot be recorded in it. An operator reading the waivers section will believe it is exhaustive. Widening the reader to match prose would be worse - a detector guessing at intent - so the fix belongs in what `waive` can express.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0926 ships - planning: SUPERSEDED - gate stood down in prose invisible to waiver disclosure: batch 2 deletes the stood-down gates, leaving nothing to disclose; superseded only once US0926 ships (D0264) |
