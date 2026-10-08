# BG0990: reconcile's field sync reads a '·'-joined metadata run to end of line, writing 'P2 · **Type:** ...' into index cells and dropping the later fields

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile_inline_field_run.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, changelog.d/BG0990.md
> **Evidence:** Found in a consuming project BG0463, 2026-10-07, on the installed skill (6.1.0 plus one file from main 922b9d6c); reproduced against this repo's main 922b9d6c. the consuming project already carried the same artefact in 14 CR Priority cells and 96 bug Severity cells before that run.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T18:00:23Z

## Summary

`reconcile._file_field_values` (the field-projection pass behind `reconcile apply`) reads header fields with `_ANY_FIELD_RE = ^>?\s*\*\*([A-Za-z][A-Za-z ]*?):\*\*\s*(.*?)\s*$`, so on a metadata line that carries several fields joined by `·` the first field's value runs to end of line and the later fields are never read. `sdlc_md.extract_field` handles exactly that shape (its docstring names the `·` inline run) and stops at the next `·` or `**Field:**`. The two readers disagree on the same header: for `> **Priority:** P2 · \*\*Type:\*\* group-chat / SSE contract (additive).`, `extract_field` returns 'P2' while `_file_field_values` returns {'priority': 'P2 · \*\*Type:\*\* group-chat / SSE contract (additive).'} with no 'type' key. `reconcile apply` then writes that whole run into the index's Priority cell, `detect` keeps it stable (it compares with the same reader), and status/backlog counts that bucket by Priority or Severity misread the row.

## Steps to Reproduce

An artefact whose header has `> **Priority:** P2 · \*\*Type:\*\* x` on one line, indexed with a Priority column: `reconcile.py apply` -> the row's Priority cell reads `P2 · \*\*Type:\*\* x`. In Python: `reconcile._file_field_values(text)['priority']` vs `sdlc_md.extract_field(text, 'Priority')`.

## Proposed Fix

Make `_file_field_values` split each metadata line on the same `·` / `**Field:**` boundaries `extract_field` uses (ideally by calling one shared tokeniser), so every field on a joined line is read and none swallows the next; then a one-off `reconcile apply` repairs existing cells.

## Acceptance Criteria

- [ ] **AC1** A metadata line joining several fields with `·` projects each field to its own value, identical to `sdlc_md.extract_field` for every field on the line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile_inline_field_run.py -k each_field_projected
- [ ] **AC2** `reconcile apply` over an index whose cells hold a swallowed run rewrites them to the single field value
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile_inline_field_run.py -k apply_repairs_swallowed_cells

## Triage

- Reproduced at 124c4d08: for `> **Priority:** P2 · **Type:** x`, `reconcile._file_field_values` returns `{'priority': 'P2 · **Type:** x'}` with no `type`, while `sdlc_md.extract_field` returns `P2` and `x`. Two readers of one header disagree (LL0016). Not a regression of a recent run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: reproduced at 124c4d08, not a regression; consuming-project name generalised; changelog fragment added to Affects |
