# BG0073: migrate_v3 re-run after an interrupted apply re-mints a different id map and silently cross-wires identities

> **Status:** Open
> **Severity:** High
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: BLOCKS v4.0 tag. migrate_v3 apply rewrites every intra-workspace reference in phase 1 (migrate_v3.py:128-135), then renames files in phase 2 (:136-145), with no persisted id map or journal. The map derives from add-epoch/mtime order plus a per-file counter (:90-98); a crash between phases (or mid-phase-2) followed by a re-run re-derives a DIFFERENT assignment - phase-1 atomic_writes bumped mtimes, and already-renamed files are idempotency-skipped which shifts the counter for the rest. Reproduced (RV0007): index rows point at BG-01KX4E00/01 while files on disk are 01KX4E01/02; epic fields dangle. No error is raised. The docstring's idempotency claim (:10-11) covers only a COMPLETED run. Corrupts a consuming project on the documented v4 upgrade walk if the migration is interrupted.

## Steps to Reproduce

Fixture workspace; run migrate_v3 apply and kill it between phase 1 and phase 2 (or mid-phase-2); run apply again; compare index links/Epic fields to filenames -> swapped/dangling identities, exit 0.

## Proposed Fix

Persist the id map to .local/migrate-map.json before any write; on start, detect a partial migration and resume from the saved map (refuse to re-plan).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
