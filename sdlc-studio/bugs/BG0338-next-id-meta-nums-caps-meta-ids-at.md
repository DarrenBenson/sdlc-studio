# BG0338: next_id._meta_nums caps meta ids at 4 digits, re-minting ids past 9999 - the widened sdlc_md.id_number fix was never por

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_next_id.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_d141ccb5

## Summary

The meta-id reader (retro/review/handoff) parses at most 4 digits, so RETRO10000 reads back as 1000, `allocate_number` computes max=9999 and mints 10000 again; with a different title slug the path.exists() guard does not fire and a duplicate id lands. `id_number` was deliberately widened to 4-7 digits for exactly this class (BG0199 covered only the lower boundary) and the shared-regex remedy was not taken.

## Steps to Reproduce

Evidence (`_meta_nums`, lines 45-49; contrast `sdlc_md.py` `id_number` lines 1252-1263): Confirmed: `next_id.py` 48 pattern is prefix + (\d{3,4}); `index_row_ids` returns [] for meta types so nothing backstops the re-mint; `sdlc_md.id_number(`'US10000') returns 10000.

## Proposed Fix

Widen the `_meta_nums` pattern to \d{3,7} to match `id_number`'s range, ideally by extracting one shared id-digits regex into lib/`sdlc_md.py` that both readers use, per BG0199's original proposed remedy.

## Acceptance Criteria

### AC1: a meta id past 9999 reads back whole

- **Given** `sdlc-studio/retros/RETRO10000-x.md` on disk
- **When** the allocator reads the meta ids
- **Then** it reports 10000, not the 1000 the four-digit cap truncated it to
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::MetaIdWidthTests::test_five_digit_meta_id_reads_back_whole

### AC2: the allocation above a truncated id is not an id already on disk

- **Given** RETRO10000 and RETRO01001 both on disk (the truncation collapses them to 1000 and 100)
- **When** `allocate_number("retro")` runs
- **Then** it returns 10001, not the 1001 that RETRO01001 already holds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::MetaIdWidthTests::test_allocation_above_a_five_digit_id_does_not_re_mint_a_live_id

### AC3: the meta reader admits the same digit range as `sdlc_md.id_number`

- **Given** a seven-digit meta id, the top of `id_number`'s widened range
- **When** both readers are asked for its number
- **Then** they agree - the two cannot disagree about what an id is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::MetaIdWidthTests::test_seven_digit_meta_id_matches_id_number_range

### AC4: a digit run past the range is ignored, never truncated

- **Given** an eight-digit stem, past what a sequential id can be
- **When** the allocator reads it
- **Then** it is skipped, as `id_number` skips it - widening the cap without refusing a longer
  run would only move the truncation, and to a number no file holds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::MetaIdWidthTests::test_a_digit_run_past_the_range_is_ignored_not_truncated

### AC5: ordinary four-digit meta ids are untouched

- **Given** `HO0007` and `HO-0009` (both minted forms)
- **When** the allocator reads and allocates
- **Then** it sees [7, 9] and returns 10, exactly as before the widening
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::MetaIdWidthTests::test_four_digit_ids_are_unaffected

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | Claude Opus 5 (sprint RUN-01KYJZGZ) | Reproduced, acceptance criteria authored, `_META_ID_DIGITS` widened to `id_number`'s range with a `(?!\d)` guard against silent truncation |
