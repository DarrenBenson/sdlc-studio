# BG0889: A padded index table holding a wide character still fails MD060 after a row in it is rewritten

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** BG0867 QA review round 2 (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T19:08:32Z

## Summary

BG0867 re-aligns only the table a write touched and leaves any table holding a wide, combining or format character alone, because Python len() is not markdownlint's display width. A padded table holding such a character, with a row rewritten by reconcile, therefore still fails MD060, as before BG0867.

## Steps to Reproduce

1. A padded test-spec index table holding a CJK cell. 2. transition.py set one of its rows -> markdownlint MD060 on that row.

## Proposed Fix

Measure display width as markdownlint's string-width does (east-asian W/F as 2, combining and format as 0) and align those tables too.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0867 re-aligns only the table a write touched and leaves any table holding a wide, combining or format character alone, because Python len() is not...
- [ ] **AC2** The proposed fix lands, pinned by a test: Measure display width as markdownlint's string-width does (east-asian W/F as 2, combining and format as 0) and align those tables too.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
