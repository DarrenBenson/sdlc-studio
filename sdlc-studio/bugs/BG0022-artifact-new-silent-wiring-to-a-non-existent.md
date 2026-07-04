# BG0022: artifact new - silent wiring to a non-existent epic and file-only id allocation

> **Status:** Closed
> **Severity:** Medium
> **Created:** 2026-06-21

## Summary

Self-audit (CR0045 follow-up). Two correctness gaps in artifact.new: (1) a story created with --epic for a non-existent epic succeeds with epic_linked=false and no warning - an orphaned story whose dangling link only surfaces at the next integrity run. (2) id allocation uses the FILE census only (file_finding._next_number -> next_id.local_ids), so it ignores remote/history and stale index rows - it can re-issue an id that exists on origin/main or as an archived index row, producing a duplicate.

## Steps to Reproduce

new --type story --epic EP9999 -> created, epic_linked=false, exit 0. And: delete a story file but keep its index row -> new reissues that id.

## Proposed Fix

Warn/raise when a story's parent epic is absent; route allocation through next_id honouring remote_max + existing index rows, not the file census alone.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | audit | Filed |
| 2026-06-21 | Autosprint (BG0022) | Fixed: raise on absent epic (pre-write); allocate_number honours index rows + origin/main; critic APPROVE |
