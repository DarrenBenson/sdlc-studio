# BG1473: A damaged tracked run record reads on the brief as awaits its run's signature, not as damaged

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG1473.md
> **Evidence:** QA seat's round-2 review of US1068, run thirteen (sdlc-studio/reviews/verdicts/US1068/50b808f82d31-827ff2f0.txt), probed at 9ebfb692.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:50:36Z

## Summary

`run_state.signed_record` turns RunStateError into None (near line 698), so a learning whose run's tracked record cannot be parsed reads on a seat's brief as 'awaits its run's signature'. `read_tracked` says a damaged signed record is not the same fact as an absent one. The behaviour is fail-safe, since the learning is not carried, but the brief gives the operator the wrong reason, and a damaged signed record goes unnoticed.

A run record that is not UTF-8 is the same damage reached by another path: `lib/run_state.py` `archived` (line 525) and `read_tracked` (line 670) read it as UTF-8 and raise `UnicodeDecodeError`, which `_run_record` and `_run_state_for` do not catch, so the command ends in a traceback rather than naming the record as damaged (found by run twenty-two's lane P, 2026-11-22).

## Steps to Reproduce

1. Sign a run whose listed learning goes live.
2. Corrupt the tracked record's JSON.
3. Brief the seat: the learning reads 'awaits its run's signature'.

## Proposed Fix

Have `signed_record` return a distinct damaged state, and have the brief and the close name the record as unreadable, with its path.

## Acceptance Criteria

- [ ] **AC1** Given a signed run whose listed learning is live, and its tracked record then corrupted so it no longer parses, when the seat is briefed, then the brief says the run's record is unreadable and names its path, and the learning is not carried. Fails on: the damaged record reading as awaits its run's signature.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_a_damaged_run_record_is_named_as_unreadable_on_the_brief
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given a learning whose run's record is readable and unsigned, or absent, when the seat is briefed, then it still reads as awaiting its run's signature and names no damage. Fails on: the damaged state reported for a record that is only unsigned or absent.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py::StrikeLearningTests::test_an_unsigned_or_absent_record_still_awaits_its_signature
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given a tracked run record whose bytes are not UTF-8, when `read_tracked` or `signed_record` reads it, then `RunStateError` (or the unreadable state) names its path, with no traceback. Fails on: `read_tracked` catches OSError and JSONDecodeError only, so `UnicodeDecodeError` escapes (reproduced at HEAD cecc9dfe7: both `read_tracked` and `signed_record` raise it).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::TrackedRecordTests::test_a_non_utf8_record_is_named_as_unreadable
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Summary notes the non-UTF-8 run record's decode traceback in `run_state.py`, the same damage by another path |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: added the non-UTF-8 path as AC3, tests/test_run_state.py named; 2 pts |
