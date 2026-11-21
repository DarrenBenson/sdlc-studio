# BG1208: BG1122's meter memo leaves the unfinished-line size refresh unpinned, and its changelog's equals-a-whole-read claim holds only for append-only growth

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_meter_incremental_read.py, CHANGELOG.md, changelog.d/BG1208.md
> **Evidence:** BG1122 round-1 verdict, scratchpad run5/BG1122-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T15:18:54Z

## Summary

2026-11-04, BG1122's review (qa-seat-BG1122-r1, APPROVE, non-blocking). The mutant `if held is None or cut:` at `run_state.py`:1039 passes all 12 tests of `test_meter_incremental_read.py`; in isolation a partial line grown then truncated below the bytes last read is resumed by the mutant where the shipped code re-reads whole. Separately, changelog.d/BG1122.md:11 says a resumed reading equals one that parses every file whole, but an in-place mid-file rewrite with both 4 KiB ends unchanged reads 288006000 against a whole read's 288014000. The harness's transcripts are append-only, so totals are unaffected in practice.

## Steps to Reproduce

1. Apply the `run_state.py`:1039 mutant and run `test_meter_incremental_read.py`: all pass.
2. Rewrite one record mid-file in a memoised transcript, same size and ends, and compare a resumed reading with a whole one.

## Proposed Fix

Pin the size refresh for a grown unfinished line, and scope the changelog sentence to append-only growth.

## Acceptance Criteria

- [ ] **AC1** The `run_state.py`:1039 mutant fails a test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_incremental_read.py

## Impact

A later edit can drop the refresh with the suite green, and the changelog over-states the guarantee.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. The meter memo is correct for append-only growth, the only shape a transcript takes; the size-refresh mutant and a changelog sentence are unpinned. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
