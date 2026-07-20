# BG0216: A lesson gist containing bold markup makes the lessons-summary gate unsatisfiable

> **Status:** Fixed
> **Verification depth:** functional (the digest comparison normalises emphasis, so the render/parse round trip is stable for a lesson whose own text carries bold; proven end to end by restoring the exact wording that deadlocked the RETRO0057 close - the lane is green with no reword, and a mutant dropping the normalisation is killed by two tests, one of which checks the comparison still notices a real one-word edit)
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

LESSONS-SUMMARY.md renders each lesson as a bullet wrapped in bold. When the lesson gist ITSELF begins with bold markup, the round trip is not stable: the generator writes the nested emphasis one way and `parse_summary_digest` reads it back with the emphasis spanning the whole line. `summary_status` then reports the SAME lesson as both added and removed, so the blocking lessons-summary gate lane fails, and running lessons.py summary does not fix it - the generator and the parser disagree by construction. The lane has no satisfying state and blocks sprint close. Only manifests on a gist short enough to escape truncation, which is why sibling lessons with the same markup do not trip it.

## Steps to Reproduce

1. Record a lesson whose gist starts with bold markup and is short enough not to be truncated in the digest. 2. Run lessons.py summary to regenerate LESSONS-SUMMARY.md. 3. Run the close gate, or `lessons.summary_status.` 4. The lane reports STALE, naming the same lesson id in both the added and the removed list. 5. Regenerating again changes nothing.

## Proposed Fix

Make the digest round trip on the gist text rather than on its rendering: strip or escape emphasis when composing the bullet, or compare on a normalised form that ignores markup. Add a test that round-trips a gist containing bold, and one containing a trailing period, through `digest_items` and `parse_summary_digest.` Worked around in RETRO0057 by rewording the lesson to contain no markup, which is not a fix - the next lesson written with emphasis re-blocks the close.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
