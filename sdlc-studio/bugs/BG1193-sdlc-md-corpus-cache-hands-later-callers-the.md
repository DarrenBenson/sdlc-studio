# BG1193: sdlc_md.corpus_cache hands later callers the path spelling of the first walk, so a relative root then an absolute one raises ValueError in reconcile

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_corpus_cache_roots.py, changelog.d/BG1193.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** BG1183 builder report, 2026-11-03, outside-the-unit item 3.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T08:55:49Z

## Summary

2026-11-03, BG1183's first build (run five). Inside `sdlc_md.corpus_cache()` (lib/`sdlc_md.py`:1937) the cached walk keeps the root spelling its first caller used. A relative root followed by an absolute one makes `reconcile._census_filenames` (reconcile.py:391) raise `ValueError` when it relativises one spelling against the other. BG1183's migrate change works around it by making its root absolute before entering the cache; any other caller that mixes spellings inside the cache still fails.

## Steps to Reproduce

1. Inside `with sdlc_md.corpus_cache():`, read the stories once through a relative root (`Path('.')`).
2. Call `reconcile._census_filenames('story', Path.cwd())` with the absolute root.
3. It raises ValueError.

## Proposed Fix

Key the cache on the resolved root and hand each caller paths under the root it passed, or resolve every root on entry to the cache.

## Acceptance Criteria

- [ ] **AC1** Inside `corpus_cache()`, a relative-root read followed by an absolute-root `reconcile._census_filenames` returns the same names as outside the cache, with no ValueError.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_corpus_cache_roots.py

## Impact

A caller that wraps work in the corpus cache crashes on a mixed root spelling, which steers callers away from the cache that makes them fast.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
