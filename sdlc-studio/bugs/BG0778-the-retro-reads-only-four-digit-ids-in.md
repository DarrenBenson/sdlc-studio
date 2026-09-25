# BG0778: The retro reads only four-digit ids in dispositions and carried rows, so a v3 project's ULID ids are dropped

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:43:47Z

## Summary

`retro.ARTEFACT_ID_RE` (retro.py:172) matches only (CR|BG|US|RFC|EP|LL)-?NNNN. A fresh v6 project is schema v3 and mints ULID ids, so retro dispositions and carried-issue rows naming them are not read. Same class as the Batch grammar US0951 fixed with `BATCH_ID_RE.` Found by US0951's builder.

## Steps to Reproduce

1. init a fresh project (schema v3). 2. write a retro whose disposition or carried-issue row names a ULID id. 3. the retro's readers skip it.

## Proposed Fix

Reuse the id grammar US0951 introduces (`BATCH_ID_RE`, or the shared `sdlc_md` id pattern) for `ARTEFACT_ID_RE`, with a v3 fixture test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `retro.ARTEFACT_ID_RE` (retro.py:172) matches only (CR|BG|US|RFC|EP|LL)-?NNNN.
- [ ] **AC2** The proposed fix lands, pinned by a test: Reuse the id grammar US0951 introduces (`BATCH_ID_RE`, or the shared `sdlc_md` id pattern) for `ARTEFACT_ID_RE`, with a v3 fixture test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
