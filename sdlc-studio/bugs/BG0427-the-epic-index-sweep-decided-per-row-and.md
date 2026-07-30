# BG0427: the epic-index sweep decided per row and wrote per epic id, resolved the header by one literal spelling, and read an unparseable dependency row as a declaration of none

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** Found by an independent adversarial review of US0477/US0478. Two of the three were demonstrated to destroy unrelated columns (a Reviewer and Sign-off cell replaced with a story count and an epic id).
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (from the independent review of US0477/US0484); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z
> **Verification depth:** functional

## Summary

Three defects in the same sweep. (1) `apply` classified each cell per ROW but keyed its writes by epic id, so on a multi-view index one row's fillable verdict acted on another row's held cell: apply printed 'left alone' for a cell and then wrote over that very cell, returning the same key in both `synced` and `held`. (2) The header was located with `startswith('| ID |')`, which resolves to nothing for a padded, unspaced or indented header - a silent no-op reporting clean on a fully drifted index - and on a multi-table index lent the first table's offsets to a second table's rows, writing a story count into whatever column sat there. (3) An unparseable `## Dependencies` row was read as `[]`, i.e. 'the epic declares it has none': an epic minted from the full template therefore declared no dependencies on the strength of an unrendered placeholder row, and a cell naming two ids silently dropped one.

## Steps to Reproduce

1. Build an index listing one epic in two tables, one row fillable and one held - apply warns about the held cell and writes it anyway.
2. Pad the header to `| ID     | Title |` - drift reports empty on a drifted index, apply writes nothing, no warning.
3. Mint an epic with the full template and read its Deps cell - `None`, from an unrendered placeholder.

## Proposed Fix

FIXED. Writes are keyed by LINE and a reported cell names its row (`EP0001.Stories@L12`). Tables are identified by their separator row rather than a header spelling, and each row resolves its columns against the table that contains it. An unparseable dependency row returns unknown; an explicit `| None |` row is still a declaration; a second table inside the Dependencies section is not read as dependencies; a two-id cell is unresolvable rather than truncated.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Three defects in the same sweep.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (from the independent review of US0477/US0484) | Filed |
