# BG0090: gate.py fail-open: a check that raises is recorded non-blocking and the gate prints PASS

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (needs a buggy/crashing check to fire - and BG-KeyError-date is exactly that today: gate --only index-derived over a drifted workspace prints '[warn] check raised, skipped: date' and PASSES, exit 0). gate.py:255-265 catches any non-ConventionsError exception from a check and appends it as status='error', blocking=False; :265's ok = all(blocking results) then excludes it from the PASS calculation. A would-be-blocking check that crashes converts a red gate to green - the BG0059 vacuous-PASS class at a new location. Reproduced twice (RV0007).

## Steps to Reproduce

gate.py --only index-derived --root <workspace with a missing dated index row> -> [warn] index-derived: check raised, skipped: 'date' -> gate: PASS, exit 0.

## Proposed Fix

A raised check fails the gate when its registry entry is blocking (keep advisory lanes warn-only).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
