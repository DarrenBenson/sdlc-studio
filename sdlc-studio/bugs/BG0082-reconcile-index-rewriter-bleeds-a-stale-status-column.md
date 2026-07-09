# BG0082: reconcile index rewriter bleeds a stale Status column into following status-less tables, corrupting author-maintained cells

> **Status:** Open
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (shipped templates escape by column geometry; custom layouts are corrupted silently). `_rewrite_index_lines` (reconcile.py:723-758) never resets status_col/id_col when a header `_header_kind` cannot classify (:656-669) passes, so the previous data table's column indices stay live across e.g. a Dependencies table. Reproduced and adversarially verified (RV0007): with a 3-column master, apply rewrote a following table's Notes cells both ways ('Done' -> 'Blocked' and 'Blocked until auth review lands' -> 'Done'). Precondition refinement: the :697 guard skips non-status-shaped cells, but canonical_status is PREFIX-matched (sdlc_md.py:511), so any note beginning with a vocab word is a casualty.

## Steps to Reproduce

Index with ID|Title|Status master then a Story|Depends on|Notes table whose Notes cell starts with a status word; introduce a status fix for a master row; reconcile apply -> the Notes cell is rewritten.

## Proposed Fix

Reset status_col/id_col/in_summary on any header row `_header_kind` cannot classify.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
