# BG0187: TRD 9 threat model still calls plan.py archive the sole write exception, contradicting rule 5

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/trd.md
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

TRD 9 Threat Model row reads 'plan.py archive is the sole, bounded exception' to writes-confined-to-.local, but 5 rule 5 (enriched by US0210) now lists archive/retro/handoff/transition/`persona_gen`/decisions as committed-file writers. The two sections contradict. Found by the EP0071 closing review.

## Steps to Reproduce

Read TRD 9 Threat Model 'Script mutating files outside its remit' row, then read 5 rule 5's writer list - the 9 row claims a sole exception the 5 list contradicts.

## Proposed Fix

Restate the 9 row to point at the 5 rule 5 writer set, or drop the 'sole exception' wording.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
