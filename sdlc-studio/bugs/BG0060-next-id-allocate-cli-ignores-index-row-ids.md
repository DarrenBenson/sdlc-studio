# BG0060: next_id allocate CLI ignores index-row ids and defaults remote off, diverging from allocate_number

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

The `next_id.py allocate` CLI subcommand re-implements id allocation instead of calling the
library `allocate_number`, dropping the stale-index-row and archive-row protection and
inverting the remote default. The CLI is the documented contract agents are told to use.

## Evidence

- `.claude/skills/sdlc-studio/scripts/next_id.py:101-111` - `allocate_number` takes the max
  over local files, index rows (incl. archives), and remote; `remote=True` default; its
  docstring: "a deleted-but-still-indexed id ... is never re-issued".
- `next_id.py:142-156` - `cmd_allocate` computes `base = max(local_max, remote_max)` with no
  `index_row_ids`, and `--remote` is opt-in (default off).
- `reference-scripts.md:399-409` - tells agents to run `next_id.py allocate`.

## Impact

The public CLI can re-issue an id whose file was deleted but whose index (live or archived)
row remains, and by default ignores origin/main - minting the duplicate-id collision the
`duplicate-id` gate then has to catch after the fact. The programmatic path (artifact.py /
file_finding.py via `allocate_number`) is safe, so the two allocators disagree.

## Steps to Reproduce

1. Delete an artefact file whose index row remains (or leave an archived row).
2. `python3 next_id.py allocate --type cr` returns a number at or below the deleted id.
3. `allocate_number("cr", root)` returns a higher, collision-free number.

## Proposed Fix

Make `cmd_allocate` call `allocate_number(type_, root, remote=args.remote)` (single
authority), deriving the warning text from its components. Related divergence in the
programmatic path is not present; this is CLI-only.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; corroborated by both code-level and architecture legs |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
