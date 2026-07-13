# BG0119: engagement-floor uses two different file recognisers for the declared-boolean and the file-count

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson; persona; v1

## Summary

Found by the BG0118 review (2026-07-13), non-blocking, latent. The engagement floor recognises a declared Affects footprint two different ways. `_affects_declared` (which sets the declared boolean that decides undeclared-vs-not) uses the broadened `_is_file_token`, accepting extension-less real files. But `_declared_source_files` (which computes the file COUNT that decides multi-file-vs-single) uses `sdlc_md.affects_files`, whose recogniser is narrower (only /-bearing tokens or a fixed extension set .py/.md/.yaml/.yml/.sh). So a bare `Affects: Makefile` reads as declared true yet contributes 0 to `source_files`. Harmless within a single-file change (0 < threshold, and the git union still cross-checks understatement), but it is a real inconsistency: the same field is parsed by two recognisers that disagree, and the next change in this area can trip on it. BG0118 fixed the declared-boolean recogniser; this unifies the two.

## Steps to Reproduce

1. A unit declaring Affects: Makefile (extension-less real file). 2. `_affects_declared` -> declared=True (post-BG0118). 3. `_declared_source_files` via `sdlc_md.affects_files` -> 0 files counted. The two recognisers disagree on the same input.

## Proposed Fix

Route both `_affects_declared` and `_declared_source_files` through ONE recogniser (extend `sdlc_md.affects_files` to the BG0118 extension-less/dotfile logic, or have both call `_is_file_token)`, so the declared boolean and the file count never disagree about what counts as a real footprint.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Sam Eriksson | Filed |
