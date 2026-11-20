# BG1667: persona_resolve.py resolve tracebacks with UnicodeDecodeError on a seat card that is not valid UTF-8, where critic.py brief refuses it cleanly

> **Status:** Open
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

- [ ] **AC1** The behaviour described is corrected: US1055's engineering review (RUN-01M7VNR0) found that a seat card holding bytes that are not valid UTF-8 makes `persona_resolve.py` resolve --seat qa exit 1...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Write a project seat card sdlc-studio/personas/seats/qa.md containing a byte such as 0xff, then run python3...
- [ ] **AC3** The proposed fix lands, pinned by a test: Read seat cards through `sdlc_md.read_text_safe` (or catch UnicodeDecodeError where the card is read) and refuse with the card's path and a one-line remedy...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
