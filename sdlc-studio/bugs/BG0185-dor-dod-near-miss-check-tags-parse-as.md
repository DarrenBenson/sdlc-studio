# BG0185: DoR/DoD near-miss check tags parse as no-tag instead of erroring

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/validate.py
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

`sdlc_md.CHECK_TAG_RE` matches lowercase-only, so a near-miss tag (wrong case / spacing) silently parses as no-tag and the check is unenforced rather than flagged - a silent control failure (was CR0332).

## Steps to Reproduce

Write a DoR/DoD item with a mis-cased or mis-spaced [Check: ...] tag; the parser matches nothing and the item reads as carrying no check tag, so the criterion is silently not enforced.

## Proposed Fix

Detect a near-miss (a bracketed token close to the check-tag shape) and ERROR loudly - the exact class the tag registry exists to close - rather than parsing as absent. Add a near-miss test.

## Resolution

`CHECK_TAG_RE` matched lowercase-only, so a mis-cased/mis-spaced tag parsed as no-tag and its criterion went silently unenforced. Added `check_tag_near_misses` (a case-insensitive `[ check ... ]` shape the strict parser rejects) and wired it into `validate.py`'s DoR/DoD check as a loud `malformed-check-tag` ERROR. Verified functionally: a `definition-of-done.md` carrying `[Check: story.verify-ac]` now fails validate with the token named; a valid tag and an unrelated `[checkpoint: 3]` do not flag. Repo-wide validate stays errors=0.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
| 2026-07-17 | claude-opus-4-8 | Fixed: near-miss detector + loud validate error |
