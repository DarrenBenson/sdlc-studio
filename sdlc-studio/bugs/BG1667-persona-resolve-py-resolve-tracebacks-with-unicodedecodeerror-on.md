# BG1667: persona_resolve.py resolve tracebacks with UnicodeDecodeError on a seat card that is not valid UTF-8, where critic.py brief refuses it cleanly

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T13:06:29Z

## Summary

US1055's engineering review (RUN-01M7VNR0) found that a seat card holding bytes that are not valid UTF-8 makes `persona_resolve.py` resolve --seat qa exit 1 with a UnicodeDecodeError traceback, at the base ref 958701b5 as at HEAD. critic.py brief refuses the same card with a clean message. Pre-existing: US1055's diff did not introduce it.

## Steps to Reproduce

Write a project seat card sdlc-studio/personas/seats/qa.md containing a byte such as 0xff, then run python3 .claude/skills/sdlc-studio/scripts/`persona_resolve.py` resolve --seat qa --render review: it prints a UnicodeDecodeError traceback and exits 1.

## Proposed Fix

Read seat cards through `sdlc_md.read_text_safe` (or catch UnicodeDecodeError where the card is read) and refuse with the card's path and a one-line remedy, exiting non-zero, as critic.py brief does; pin it with a test.

## Acceptance Criteria

- [x] **AC1** The behaviour described is corrected: US1055's engineering review (RUN-01M7VNR0) found that a seat card holding bytes that are not valid UTF-8 makes `persona_resolve.py` resolve --seat qa exit 1...
- [x] **AC2** Following the recorded steps no longer reproduces the defect: Write a project seat card sdlc-studio/personas/seats/qa.md containing a byte such as 0xff, then run python3...
- [x] **AC3** The proposed fix lands, pinned by a test: Read seat cards through `sdlc_md.read_text_safe` (or catch UnicodeDecodeError where the card is read) and refuse with the card's path and a one-line remedy...

## Resolution

Fixed in passing by 95eb3f92 (US1056, US1057 and US1322's repair, RUN-01M7VNR0), which reads each seat card safely where it is read. Re-checked at 81e02369 under D0563 and not refuted by an independent engineering seat: a fixture seat card holding a 0xff byte makes `persona_resolve.py` resolve (review, build, json and path-only), resolve-consult (both modes) and panel (refine and triage) exit 1 with the card-not-utf8 refusal and its 'save it as UTF-8' remedy, with no traceback (AC1, AC2). The resolver's read is pinned by `test_persona_standard_mode.test_a_sibling_seat_card_that_is_not_utf8_leaves_both_modes_working`, whose mutant restores the strict UTF-8 read (AC3).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (qa seat, delegate under D0545) | Fixed: re-check under D0563 found it fixed by 95eb3f92; the engineering refute failed; criteria ticked with the evidence in Resolution |
