# BG0225: the close-owed detector misses a unit written in parentheses on the retro Batch line

> **Status:** Fixed
> **Severity:** Low
> **Verification depth:** functional (6 tests covering parenthesised, bare, punctuation-adjacent, five-digit and lookalike ids; 4 separate defects re-introduced and each killed a named test; asserted on the rendered report rather than the helper, since the correct effect here is a unit ceasing to be falsely reported)
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The detector token-matches ids in the retro's Batch field. A Batch line reading 'BG0219, EP0090 (US0276)' - a natural way to write a story delivered under its epic - matches BG0219 and EP0090 but not US0276, so the advisory kept firing for a unit whose retro genuinely names it. Observed live while settling the RETRO0059 interstitial close: the line had to be reworded to the flat comma form before the advisory cleared.

## Steps to Reproduce

1. Close units BG0001, EP0001, US0001 with a retro whose Batch line reads 'BG0001, EP0001 (US0001)'. 2. Run status. 3. The close-owed advisory still names US0001 although the retro's Batch names it.

## Proposed Fix

Extract ids from the Batch line with the standard id-search regex over the whole line rather than comma-token equality, so parenthesised, bracketed or prose-embedded ids count.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
