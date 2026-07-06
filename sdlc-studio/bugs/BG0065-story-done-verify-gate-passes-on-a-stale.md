# BG0065: story Done verify gate passes on a stale merged report entry: edited ACs keep last week's green

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

The story-to-Done verify gate looks up the story's entry in a merged, accumulating
`verify-report.json` and blocks only on `failed`/`stale` counts. Entries carry no timestamp
and the gate never compares the entry's AC count against the story's current ACs, so a story
verified green, then edited to add or change an AC, still passes on the old entry.

## Evidence

- `.claude/skills/sdlc-studio/scripts/transition.py:104-124` - `_done_verify_gate` blocks
  only on `entry.get("failed")` / `entry.get("stale")`.
- `.claude/skills/sdlc-studio/scripts/verify_ac.py:524-560` - `write_report` merges by
  default ("verifying a sprint one story at a time accumulates"); entries carry no timestamp.
- The gate never re-parses the story's current executable-AC count nor compares the story
  file's mtime against the report.

## Impact

The Done gate is the product's headline claim ("a story only reaches Done when its criteria
pass"). Stale-pass - a story green last week, then given a new AC4 or a changed AC2 Verify
line - is exactly the failure mode the gate exists to prevent.

## Steps to Reproduce

1. Verify a story green into the merged report.
2. Edit the story to add AC4 (never verified) or change an existing AC's Verify line.
3. `transition.py set --id US0001 --status Done` passes on the stale entry.

## Proposed Fix

Have `_done_verify_gate` re-parse the story's current executable-AC count and block on a
mismatch against the entry's `ac_count` (already recorded). Additionally stamp per-entry
`verified_at` and block when the story file's mtime is newer.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; filed from RV0006 architecture leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
