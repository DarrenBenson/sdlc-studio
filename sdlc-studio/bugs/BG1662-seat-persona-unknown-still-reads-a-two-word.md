# BG1662: seat-persona-unknown still reads a two-word product surface marked with a role, such as Ship the Admin Console (Primary), as an unknown persona

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T10:14:33Z

## Summary

BG1655's repair builder (RUN-01M7VNR0) found one misread its AC4 does not cover: 'Ship the Admin Console (Primary)' warns seat-persona-unknown naming Admin Console, because under D0554 and D0556 a run of two capitalised words reads as a full name and nothing syntactic tells a product surface from a person. The rule blocks under US1052's standard, so a seat card worded this way is refused, though the refusal names the line and a one-line reword clears it. Graded Low on likelihood: the remaining misreads need a capitalised two-word noun phrase directly before a bracketed role. If more appear, the remedy is to make seat-persona-unknown reported rather than blocking.

## Steps to Reproduce

In a cast of Maya Okafor, give a seat card the line 'Ship the Admin Console (Primary) before the reports page' and run validate.py seats: it warns seat-persona-unknown naming Admin Console, and `persona_review.py` check exits 1.

## Proposed Fix

Read a bracketed role after a run as a persona claim only when the run is introduced as a persona (the word persona, or a cast role phrase, nearby), or report rather than block an unresolved name.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1655's repair builder (RUN-01M7VNR0) found one misread its AC4 does not cover: 'Ship the Admin Console (Primary)' warns seat-persona-unknown naming Admin...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a cast of Maya Okafor, give a seat card the line 'Ship the Admin Console (Primary) before the reports page' and run validate.py seats: it warns...
- [ ] **AC3** The proposed fix lands, pinned by a test: Read a bracketed role after a run as a persona claim only when the run is introduced as a persona (the word persona, or a cast role phrase, nearby), or report...

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. A two-word surface marked Primary warns once; workaround is to reword.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
