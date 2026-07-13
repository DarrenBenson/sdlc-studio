# BG0121: the meta-index bootstrap path lacks the blank-collapse and the index lint guard skips meta templates

> **Status:** Open
> **Severity:** Low
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson; persona; v1

## Summary

Found by the BG0120 review (2026-07-13), two non-blocking completeness gaps that interact with BG0116. First: `artifact._ensure_meta_index` (the retro/review/handoff bootstrap BG0116 added) duplicates the drop-sample-rows logic but did NOT receive BG0120's blank-collapse, and its docstring still claims it mirrors `file_finding.ensure_index` - which it no longer does. Latent MD012 risk if any meta index template ever gains a mid-body sample row; currently safe only because retro/review/handoff templates keep the sample row trailing. Second: BG0120's round-trip markdownlint index leg iterates only `NEW_TYPES` (the 8 pipeline types), so the review.md and retro.md meta templates - the two this wave touched most - are unguarded, and a regression to them would escape the guard despite the test's docstring implying it protects a consuming project's first index of a type.

## Steps to Reproduce

1. Read `artifact._ensure_meta_index` vs `file_finding.ensure_index`: the blank-collapse is in one, not the other. 2. Read the round-trip index leg: it iterates `NEW_TYPES` (8 pipeline types), not the meta types.

## Proposed Fix

Route both bootstrap paths through one shared index-writer helper that carries the blank-collapse (so `ensure_meta_index` genuinely mirrors `ensure_index)`, and extend the round-trip markdownlint index leg to also cover the meta index templates (retro/review/handoff).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | Sam Eriksson | Filed |
