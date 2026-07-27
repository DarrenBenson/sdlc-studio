# BG0342: All four artefact indexes assert stale Last Updated stamps that no writer maintains

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/stories/_index.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The indexes are documented as fully derived and reconcile syncs rows and counts, but nothing maintains the Last Updated header, so each index claims a freshness up to five weeks older than rows it contains, and reconcile detect reports `drift_items`=0 because the stamp sits outside every drift check - a false metadata assertion in the ledger files agents are told to trust.

## Steps to Reproduce

Evidence (Line 3 (Last Updated header) in stories/, epics/, bugs/, and change-requests/ _index.md): stories/_index.md line 3 says 2026-06-20 vs rows dated 2026-07-27; epics 2026-07-16 vs 2026-07-27; bugs 2026-07-04 vs 2026-07-26; change-requests 2026-07-04 vs 2026-07-27.

## Proposed Fix

Have every index writer (artifact.py row insertion and reconcile apply) stamp Last Updated with today's date on any row change, and add a reconcile detect check flagging a header older than the newest row's Updated date.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
