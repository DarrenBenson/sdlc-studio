# BG0956: transition set reports index synced but leaves archived index rows stale, and reconcile apply refuses them

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Evidence:** homelab 2026-10-06: 94-bug close batch; 31 archive rows hand-synced afterwards
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T17:18:27Z

## Summary

Closing 94 Fixed bugs in homelab with `transition.py set --id ... --status Closed` (skill 6.1.0+12) printed `index synced=True` for every unit, but 31 of them have their row in the archive sub-index (sdlc-studio/bugs/archive/v1.0.0/bug.md, written by archive.py), and those rows still read `Fixed`. `reconcile detect` then reports 31 status-mismatch plus a count-mismatch, and `reconcile apply` changes 0 rows: 'row not in a rewritable layout; edit it by hand'. The archive table has the same header as the live index (ID | Title | Severity | Priority | Status | Epic | Story | Created), so the layout is not exotic - the writers simply do not cover archive files while the census (`parse_index`'s union) does read them. Net effect: every transition of an archived unit creates drift that only a hand edit clears, and the sync flag claims otherwise.

## Steps to Reproduce

1. archive.py archive --type bug --release v1.0.0 with some Fixed rows
2. transition.py set --id <archived Fixed bug> --status Closed -> 'index synced=True'
3. The archive row still says Fixed; reconcile detect -> status-mismatch
4. reconcile apply -> 'could not apply ... row not in a rewritable layout; edit it by hand'

## Proposed Fix

Teach the index row writer used by transition and reconcile apply to locate a unit's row in archive sub-indexes too (the same union `parse_index` reads), and make `index synced` false when no row was written. Add a test with an archived row.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Closing 94 Fixed bugs in homelab with `transition.py set --id ...
- [ ] **AC2** The proposed fix lands, pinned by a test: Teach the index row writer used by transition and reconcile apply to locate a unit's row in archive sub-indexes too (the same union `parse_index` reads), and...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Filed |
