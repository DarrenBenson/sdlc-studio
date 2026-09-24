# BG0741: the stale lens is silenced by the sweep's own audit rulings, and repairing it will make every abandoned request double-report on the same day

> **Status:** Won't Fix
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py
> **Evidence:** Found by the independent engineering seat reviewing BG0722, 2026-09-22. It reproduced the double-report on a fixture - a request untouched 90+ days whose open child is idle 45+ days appears under both lenses - and confirmed zero overlap on the live corpus only because `stale` reports nothing at all. `_last_date` reads `Date`, `Created`, `Updated` and the Revision History table, which is where the audit ruling row lands.
> **Created:** 2026-09-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The `stale` lens judges a request by its own last-touched date, and a backlog sweep writes a dated `audit ruling` row onto every request it rules. That write resets the date, so `stale` reports zero on this repository today - the blindness BG0722's own Summary records. BG0722 added an `abandoned` lens that is immune, because it reads the children's dates. The two are currently disjoint ONLY because `stale` sees nothing. The day `stale` is repaired to ignore the sweep's own rulings, every request past 90 days whose open children are also past 45 will appear under both lenses at once.

## Steps to Reproduce

1. Run the triage sweep over this repository - `stale` reports zero.
2. Read any request an audit sweep has ruled: its Revision History carries a dated `audit ruling` row, and `_last_date` returns that date.
3. Build a fixture whose request is untouched 90+ days and whose open child is idle 45+ days - it appears under both `stale` and `abandoned`.

## Proposed Fix

Exclude the sweep's own `audit ruling` rows from `_last_date` when computing staleness, as the abandoned lens already does by reading children. Then decide the overlap deliberately - either suppress `stale` for a request `abandoned` already names, or state in both details that they are two readings of one request.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The `stale` lens judges a request by its own last-touched date, and a backlog sweep writes a dated `audit ruling` row onto every request it rules.
- [ ] **AC2** The proposed fix lands, pinned by a test: Exclude the sweep's own `audit ruling` rows from `_last_date` when computing staleness, as the abandoned lens already does by reading children.

## Impact

A lens that its own remedy switches off, and a second lens that will collide with it the moment the first is repaired. The collision matters because both are advisory: a reader seeing one request under two lenses cannot tell whether that is two problems or one, which is the exact reason the abandoned lens excludes the childless case.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - advisory stale lens silenced by audit rulings: note-level lens |
