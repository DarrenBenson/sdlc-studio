# BG0338: next_id._meta_nums caps meta ids at 4 digits, re-minting ids past 9999 - the widened sdlc_md.id_number fix was never por

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/next_id.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The meta-id reader (retro/review/handoff) parses at most 4 digits, so RETRO10000 reads back as 1000, `allocate_number` computes max=9999 and mints 10000 again; with a different title slug the path.exists() guard does not fire and a duplicate id lands. `id_number` was deliberately widened to 4-7 digits for exactly this class (BG0199 covered only the lower boundary) and the shared-regex remedy was not taken.

## Steps to Reproduce

Evidence (`_meta_nums`, lines 45-49; contrast `sdlc_md.py` `id_number` lines 1252-1263): Confirmed: `next_id.py` 48 pattern is prefix + (\d{3,4}); `index_row_ids` returns [] for meta types so nothing backstops the re-mint; `sdlc_md.id_number(`'US10000') returns 10000.

## Proposed Fix

Widen the `_meta_nums` pattern to \d{3,7} to match `id_number`'s range, ideally by extracting one shared id-digits regex into lib/`sdlc_md.py` that both readers use, per BG0199's original proposed remedy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
