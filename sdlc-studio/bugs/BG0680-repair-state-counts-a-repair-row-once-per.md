# BG0680: repair_state counts a repair row once per rejection sharing its date, so closed and fixed counts are doubled

> **Status:** Open
> **Closes with:** US0914 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Measured by the BG0677 grooming and its plan review, 2026-09-15; visible in this run's repair counts (e.g. 54 fixed for 27 findings on US0625).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`repair_state` joins repair rows to rejections on `verdict_date` alone; two REJECTs recorded the same day both claim the same row, so each closure is read once per rejection and closed/fixed come back doubled (2 closures read back as 4).

## Steps to Reproduce

1. Record two plan-review REJECTs on one unit the same day, under different briefs.
2. Record one repair answering both.
3. `repair_state(..., 'plan-review')` reports fixed=4 for 2 closures.

## Proposed Fix

Attribute each repair row to exactly one rejection (by brief fingerprint, not date), and count closures once.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `repair_state` joins repair rows to rejections on `verdict_date` alone; two REJECTs recorded the same day both claim the same row, so each closure is read once...
- [ ] **AC2** The proposed fix lands, pinned by a test: Attribute each repair row to exactly one rejection (by brief fingerprint, not date), and count closures once.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0914 ships - planning: SUPERSEDED - repair_state counting: repair ledger deleted in batch 2; superseded only once US0914 ships (D0264) |
