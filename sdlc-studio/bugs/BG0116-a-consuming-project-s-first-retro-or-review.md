# BG0116: a consuming project's first retro or review lands as reconcile drift (no meta index bootstrap)

> **Status:** Open
> **Target:** v4.1
> **Severity:** Low
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Dani Okafor; persona; v1

## Summary

Found while delivering CR0223 (2026-07-13). init.py creates the retros/ and reviews/ directories but no meta _index.md, and `meta_new()` does not bootstrap one, so a consuming project's FIRST retro or review creates a missing-index reconcile drift item rather than landing indexed. CR0223 fixed this for the new handoff type (generate bootstraps handoffs/_index.md from a shipped template) but deliberately did not retrofit retro/review: doing so could surprise a project that intentionally keeps no review index, so it wants its own unit and its own decision.

## Steps to Reproduce

1. init a fresh project. 2. artifact.py new --type retro --title X. 3. reconcile.py detect: missing-index drift on the retro index.

## Proposed Fix

Bootstrap the meta index on first create, as CR0223's handoff path now does - or decide explicitly that retro/review indexes are opt-in and make reconcile stop reporting their absence as drift. Either is fine; the current state (drift on a legitimate first use) is not.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Dani Okafor | Filed |
