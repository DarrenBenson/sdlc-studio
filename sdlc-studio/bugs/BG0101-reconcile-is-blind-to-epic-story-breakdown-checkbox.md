# BG0101: reconcile is blind to epic Story Breakdown checkbox drift for bug/CR units

> **Status:** In Progress
> **Verification depth:** functional (red-then-green: detect flags both directions and skips placeholder stubs, apply syncs both ways idempotently, default sweep exits 1 on breakdown drift alone; e2e - the new lane surfaced 21 real unticked boxes across EP0026/EP0027 that the old census certified clean, all synced mechanically; suite 1565)
> **Severity:** Medium
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Observed at the EP0028 close: all 9 breakdown units (6 bugs, 3 CRs) were terminal, yet every breakdown checkbox was still unchecked - and reconcile detect reported `drift_items`=0. The status cascade and the reconcile census only verify STORY units against an epic's breakdown; a bug or CR listed in the breakdown is invisible to both, so an epic can read Done with a breakdown that contradicts its units (or unchecked boxes can mask a genuinely unfinished unit). The boxes had to be synced by hand, which is exactly the hand-editing the discipline forbids.

## Steps to Reproduce

1. Create an epic whose Story Breakdown lists bug/CR units as checkboxes. 2. Drive every unit to a terminal status via transition.py. 3. Run reconcile detect: drift 0 despite every box still unchecked. 4. transition the epic to Done: no gate objects.

## Proposed Fix

Extend the epic-breakdown reconciliation to ALL unit types found in the breakdown (bug/CR/story): detect reports a checkbox whose unit is terminal but unchecked (and the inverse), apply syncs it mechanically like the story cascade already does.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
