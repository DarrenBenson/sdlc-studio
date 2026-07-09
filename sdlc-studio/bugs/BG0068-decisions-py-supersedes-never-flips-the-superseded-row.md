# BG0068: decisions.py --supersedes never flips the superseded row's status

> **Status:** Closed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Severity:** medium
> **Verification depth:** functional (unit tests)

## Summary

`decisions.py add --supersedes D0012` records the lineage on the new row's Supersedes
column but leaves the superseded decision's Status as `accepted`. The log then carries two
accepted decisions that contradict each other - live example in this repo: D0012 ("N=5
paused") and D0013 ("GO for N=5") are both `accepted`, and D0014 now supersedes D0013
which also still reads `accepted`. The declared status vocabulary
(`accepted | superseded | revisited`) exists precisely so a reader - or a delegated agent
consuming the decisions block as handoff context - can tell which decision is current
without reconstructing the chain by hand. Files-are-truth: the status column should be
derivable-true, not stale.

## Steps to Reproduce

1. `decisions.py add --decision A --rationale r` (creates Dx, accepted)
2. `decisions.py add --decision B --rationale r --supersedes Dx`
3. Observe Dx still reads `accepted` in `sdlc-studio/decisions.md`

## Proposed Fix

When `--supersedes` names an existing decision, rewrite that row's Status cell to
`superseded` in the same edit (fail loud if the id is not found - today a typo in
`--supersedes` is silently recorded). Backfill sweep for existing rows (D0012, D0013).
Unit test covering flip, unknown-id failure, and idempotency.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | claude | Found while recording D0014 |
