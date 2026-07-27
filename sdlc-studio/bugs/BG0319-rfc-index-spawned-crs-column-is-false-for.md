# BG0319: RFC index Spawned CRs column is false for at least 8 decomposed RFCs and reconcile cannot see it

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/rfcs/_index.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The column an auditor would use to detect 'Accepted RFC that never spawned work' shows '--' for RFCs that demonstrably decomposed (files carry Decomposed-into/Spawned lines), no row after RFC-0026 has ever been populated, and reconcile detect returns `drift_items`=0 against this state - the 'index is derived, reconcile syncs it' doctrine does not cover the column, so the drift will never self-heal.

## Steps to Reproduce

Evidence (Spawned CRs column (rows RFC-0005, 0013, 0033, 0034, 0038, 0043, 0044, 0052, 0053, 0055); 'Last Updated: 2026-06-25' header): RFC0005:53, RFC0013:166-169, RFC0043:4, RFC0044:4, RFC0053:4, RFC0055:4 and RFC0038:234 all name spawned CRs/epics while their index rows show '--'; live reconcile detect run: scope=all `drift_items`=0.

## Proposed Fix

Add a reconcile drift kind deriving the Spawned CRs column from each RFC file's Decomposed-into/Spawned lines, and backfill the stale rows (and the index Last Updated) via reconcile apply.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
