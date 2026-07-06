# BG0061: archive.py hardcodes its own terminal sets: Deferred stories and CRs archived as closed

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

`archive.py` defines its own TERMINAL sets that contradict the shared
`sdlc_md.TERMINAL_STATUS`, treating `Deferred` stories and CRs as terminal. The shared layer
deliberately excludes re-activatable states.

## Evidence

- `.claude/skills/sdlc-studio/scripts/archive.py:29-37` -
  `"story": {"Done", "Won't Implement", "Deferred", "Superseded"}` and
  `"cr": {..., "Deferred", ...}` (also missing "workflow").
- `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py:296-309` - `TERMINAL_STATUS` with the
  explicit comment "States that can still re-activate - Blocked, Deferred, Paused, Planned -
  are deliberately NOT terminal" and header "Derived from STATUS_VOCAB, not hardcoded at call
  sites".
- `reconcile.py:1127` uses `sdlc_md.terminal_statuses` for its own archive subcommand, so the
  two shipped archivers disagree.

## Impact

The release-based archiver moves Deferred story/CR rows out of the live index by default,
hiding live, re-activatable work; the reconcile-based archiver and the index-bloat advisory
would not. Two shipped archive commands disagree about what is safe to move.

## Steps to Reproduce

1. Have a `Deferred` CR in the live index.
2. Run the `archive.py archive` release path.
3. The Deferred row is relocated to the archive sub-index though it carries live signal.

## Proposed Fix

Replace archive.py's TERMINAL with `sdlc_md.terminal_statuses(type_)`, keeping `--statuses`
as an explicit override. (Consolidating the two archivers entirely is tracked in CR0182.)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; filed from RV0006 code-level leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
