# BG0199: two id readers disagree on width: _STEM_ID_RE needs 4+ digits, next_id._meta_nums accepts 3

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/next_id.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`next_id._meta_nums` matches a meta id of 3 OR 4 digits, so RETRO001-x.md is an id the allocator honours, but `retro._STEM_ID_RE` requires 4+ and `find_retro` will not resolve it - where the previous prefix glob did. Not reproduced against a real project (`meta_new` always formats {n:04d}, so nothing here mints a 3-digit id); reported as an inconsistency between two readers of the same id space rather than an observed failure. Found by the independent review of RUN-01KXVD74.

## Steps to Reproduce

1. Place a legacy sdlc-studio/retros/RETRO001-x.md. 2. `next_id` sees it via `_meta_nums` (\\d{3,4}). 3. `retro.find_retro(root`, 'RETRO001') returns None because `_STEM_ID_RE` requires 4+ digits.

## Proposed Fix

Settle one width rule for meta ids and share it: either widen `_STEM_ID_RE` to \\d{3,} or narrow `_meta_nums` to 4, and put the chosen regex in lib/`sdlc_md.py` so the allocator and the resolver cannot drift again.

## Regression Test

`test_a_legacy_three_digit_id_resolves` drives the reported inconsistency directly: a legacy
three-digit retro file is written, then resolved in both the dashed and undashed form. A sibling
test (`test_a_three_digit_id_still_does_not_match_a_longer_one`) pins the boundary, so widening
the width floor cannot regress into matching a longer id.

Run it with:
`python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_retro.py -k RetroIdIsResolvedInEitherForm`
(a citation, not a machine-executed `Verify:` line - only a story's Verify line is run).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
| 2026-07-19 | sdlc-studio | Fixed; regression test cited |
