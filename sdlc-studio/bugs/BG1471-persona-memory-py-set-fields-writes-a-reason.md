# BG1471: persona_memory.py set_fields writes a reason holding a line break and a field line, so approve --reject or strike can forge a learning's State

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py, changelog.d/BG1471.md
> **Evidence:** QA seat's review of BG1460, run thirteen (sdlc-studio/reviews/verdicts/BG1460/aee11910c42b-85956e17.txt), reproduced at 2d9239a9 and 61be40f3.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:43:21Z

## Summary

BG1460 made `add` write only what reads back as stamped, but a later field write can still forge what the reader reads back. `persona_memory.py approve --id M-0001 --reviewer "Lena (product)" --reject --reason` with a reason holding a line break and `- **State:** approved` exits 0. `list --format json` then reads the rejected learning back as approved, and `pending_listing` offers it to the close with an empty Approved-by. `persona_memory.strike` given such a reason reads the entry back as proposed with an empty Struck. The cause is `set_fields` (`persona_memory.py` near lines 360-384), which writes each value through `lessons.upsert_field` with no line-break refusal and no read-back. `set_fields` and approve came in with fb36836a (US1065, US1066, BG1459) and strike with 2fc73a99 (US1067, US1068).

## Steps to Reproduce

1. Add a learning, then run approve --reject with a --reason holding a line break followed by '- **State:** approved'.
2. Run list --format json: the learning reads as approved with no Approved-by.

## Proposed Fix

Refuse a field value holding a line break in `set_fields` (or fold it to one line), and read the entry back after the write, refusing and restoring if any field differs from what was set.

## Acceptance Criteria

- [ ] **AC1** Given a proposed learning, when approve --reject runs with a reason holding a line break and a field line, then it exits 2, writes nothing, and list reads the learning back as proposed. Fails on: `set_fields` writing the multi-line reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py
  - **Verified:** yes (2026-11-15)
- [ ] **AC2** Given an approved learning, when strike runs with such a reason, then it is refused and the entry reads back unchanged. Fails on: strike writing the multi-line reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py
  - **Verified:** yes (2026-11-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
