# BG0126: meta_new allocates retro/review/handoff ids without allocation_lock (concurrent collision)

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py

## Summary

new(), `new_batch()` and `file_finding()` all wrap allocate->write->index-append in `sdlc_md.allocation_lock.` `meta_new` (artifact.py:507) does not: it calls `next_id.allocate_number` (:520) and inserts the index row (:558) unguarded. Retro/review/handoff ids are ALWAYS sequential (no ULID form), which is exactly the case the lock's docstring says it most matters for. Two concurrent 'artifact new --type retro' or '--type review' (e.g. autosprint waves closing, or two review/audit runs) can allocate the same id and clobber each other's index insert.

## Steps to Reproduce

Inspect artifact.py: `allocation_lock` present at :589 (new), :679 (`new_batch)`, `file_finding.py`:261; ABSENT in `meta_new` (:507-561). Every other sequential allocator is locked; this one is the exempted path (LL0013).

## Proposed Fix

Wrap `meta_new`'s allocate+write+index-append in `sdlc_md.allocation_lock(root)`, matching the other creation paths.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
