# BG0211: an epic whose breakdown declares a dead id is owed a close no close can give

> **Status:** Fixed
> **Verification depth:** functional (all three shapes - ghost id, CR id, RFC id - reproduced red then green; guards mutation-killed; live repo answer unchanged and runtime held at 6.2s)
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

close-owed now requires every id in the union of an epic's children and its declared Story Breakdown to be covered by some retro. That union is deliberately strict - it cannot forgive more than the narrower rule - but it means an epic whose breakdown names an id with no backing file (split, renamed or deleted) or a non-delivery id (a CR or RFC) is reported as owing a close that no close can clear: nothing will ever put that id in a Batch. Reproduced three ways - a ghost id, a CR id and an RFC id in the breakdown each leave the epic owed. Zero epics are in this state on this repo today, and it errs toward over-reporting debt rather than a false zero, so it is latent rather than live. It is also recoverable by naming the dead id in a retro Batch, which is a hand edit of a generated record. The symmetric derivation refuses to derive an epic with an unresolvable child, so a Done epic in this state was transitioned by hand.

## Steps to Reproduce

1. Write a Done epic whose Story Breakdown declares an id with no backing file. 2. Cover its real children with a retro Batch. 3. Run `close_owed.py` detect. 4. Observe the epic is owed, and that no close can clear it because the dead id can never be covered.

## Proposed Fix

Either resolve declared ids before requiring coverage, treating an unresolvable or non-delivery id as not-a-child rather than as an uncovered one, or report this case as its own kind - a stale breakdown pointing at a dead id is a real defect in the epic and deserves naming as that rather than as an unpayable close debt. The second is better: it keeps the strictness and tells the operator what to actually fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
