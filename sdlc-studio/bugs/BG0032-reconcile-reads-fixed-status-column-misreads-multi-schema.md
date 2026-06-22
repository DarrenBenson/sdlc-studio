# BG0032: reconcile reads fixed status column misreads multi-schema index tables

> **Status:** Fixed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Severity:** High

## Summary

reconcile located the Status column positionally. On indexes with stacked table schemas (Status in different columns) or header-less blocks, off-schema rows read as `Unknown` -> ~78 phantom status-mismatches on a consuming project (+ contaminated counts); and apply could write the status into the wrong column.

## Steps to Reproduce

`reconcile detect`/`--apply` on a consuming project's bug/CR indexes -> ~90 phantom drifts; apply would clobber off-schema rows.

## Proposed Fix

Detect now falls back to a canonical-vocab-token scan when the pinned column holds no status (positional read still primary, preserving BG0018). Apply rewrites ONLY when the pinned column holds a status - never guesses a cell (no title clobber). Verified read-only on a consuming project: bug drift ~90->9, CR ->1 (survivors genuine).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
