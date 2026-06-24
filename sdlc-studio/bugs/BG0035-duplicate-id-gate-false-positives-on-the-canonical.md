# BG0035: duplicate-id gate false-positives on the canonical two-table story index (per-epic + All Stories)

> **Status:** Fixed
> **Severity:** high
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

reconcile.detect_duplicate_rows counts an id across ALL data tables in an _index.md, but the v3 story-index template (templates/indexes/story.md) ships TWO id-bearing tables - 'Stories by Epic' and 'All Stories' - so every story id appears twice and the gate's duplicate-id check reports N false duplicates (33 in a field project). The docstring already admits the single-table assumption. parse_index keys rows by id into a dict, so the same id across two views collapses harmlessly; the real bug the check guards (CR0055/BG0022) is an id repeated WITHIN one table. Our own repo passes only because its index happens to carry a single table.

## Steps to Reproduce

1. Scaffold a project whose stories/_index.md follows templates/indexes/story.md (per-epic tables + All Stories). 2. Run gate.py (or reconcile.detect_duplicate_rows). 3. Observe duplicate-id = (number of stories) false positives - each id counted once per view. Repro: a field agent upgrading shoppinglist to v3.0.0 saw duplicate-id: 33.

## Proposed Fix

Scope detect_duplicate_rows per-table: count an id's occurrences WITHIN each table (reset at each table header, mirroring _index_row_ids' header re-pin) and flag only ids with a within-table count > 1. The same id once-per-view across the per-epic and All Stories tables is the same story in two views, not a duplicate; an id listed twice in one table is still caught. Update the docstring; regression test both shapes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Filed |
