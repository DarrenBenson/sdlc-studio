# BG0224: an explicit --tokens 0 cannot clear a recorded velocity actual because zero is falsy in the preservation guard

> **Status:** Open
> **Severity:** Low
> **Verification depth:** functional (supplied-ness carried as its own sentinel rather than inferred from falsiness; both halves pinned - an absent --tokens preserves and an explicit --tokens 0 clears; neutering the writer branch and forcing the sentinel each killed their own test)
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`record_velocity` preserves an existing recorded actual whenever the incoming row's actual is falsy, which is right for the plain re-run case but swallows an explicit --tokens 0: the operator's documented override cannot zero out a wrongly recorded actual. The help's claim that an explicit --tokens is the override is untrue for exactly 0. Found by the independent reviewer at the RUN-01KXZQF0 close (round-2 NOTE).

## Steps to Reproduce

1. accuracy --id RETROxxxx --write --tokens 800000 (row records 800,000). 2. accuracy --id RETROxxxx --write --tokens 0. 3. The row still reads 800,000 - the explicit override was silently ignored.

## Proposed Fix

Thread the explicit-override intent to the writer (e.g. accuracy result carries `sprint_tokens_supplied)` so a supplied 0 clears the cell while an absent value still preserves; keep the plain re-run preservation exactly as is.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
