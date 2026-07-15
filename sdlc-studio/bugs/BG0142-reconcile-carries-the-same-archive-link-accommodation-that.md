# BG0142: reconcile carries the same archive-link accommodation that check_links just shed, so a regressed row could hide there

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Effort:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Points:** 2
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0137 fixed 361 wrong-depth archive row links and removed the accommodation in tools/`check_links.py` that was resolving archived rows against the TYPE DIR rather than relative to the sub-index (an accommodation added so the guard would not cry wolf over the known defect). reconcile.py has the SAME fallback, at `_link_exists`: it resolves an archive row target file-relative first, then falls back to the type dir.

It is now DEAD TOLERANCE rather than a live bug - all 361 rows resolve file-relative, so the fallback never fires. But it is the second place the wrong depth could hide, and while it stands, reconcile would not report a REGRESSED row as a dead link: a future archive writer bug would be caught by `check_links` and silently tolerated by reconcile. Two guards disagreeing about what a valid link IS, which is the LL0016 class this project keeps re-learning.

Found by the BG0137 agent and reported rather than fixed, because it was outside its file lane.

## Steps to Reproduce

1. Read reconcile.py `_link_exists` (around line 484): after the file-relative resolution it falls back to resolving an archive row target against the type dir. 2. Regress an archive row link to a bare filename (the pre-BG0137 shape). 3. tools/`check_links.py` exits 1 and names it. 4. reconcile.py detect does NOT report it as a dead-row-link, because the fallback resolves it.

## Proposed Fix

Delete the type-dir fallback from `reconcile._link_exists`, so a row link is resolved only relative to the file it sits in - which is what a readers click actually does, and what `check_links` now enforces. The two guards must agree on what a valid link is. Guard it with a test that regresses an archive row link and asserts reconcile detect reports a dead-row-link, which it currently would not.

## Acceptance Criteria

### AC1: a regressed bare-name archive link is reported as a dead link

- **Given** an archive sub-index carrying a bare-name link (`US0002-bare.md`) whose file lives in the type dir - the old wrong-depth form the type-dir fallback used to tolerate
- **When** `reconcile` detects dead row links
- **Then** it reports the row as `dead-row-link` (no fallback), agreeing with `check_links`; a correct `../../`-relative archive link still resolves
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ArchiveLinkFallbackTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
| 2026-07-15 | sdlc-studio | Fixed: removed the type-dir fallback in `_link_exists`; regression test added |
