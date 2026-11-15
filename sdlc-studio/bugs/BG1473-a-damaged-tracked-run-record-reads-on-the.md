# BG1473: A damaged tracked run record reads on the brief as awaits its run's signature, not as damaged

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_strike_learning.py, changelog.d/BG1473.md, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** QA seat's round-2 review of US1068, run thirteen (sdlc-studio/reviews/verdicts/US1068/50b808f82d31-827ff2f0.txt), probed at 9ebfb692.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:50:36Z

## Summary

`run_state.signed_record` turns RunStateError into None (near line 698), so a learning whose run's tracked record cannot be parsed reads on a seat's brief as 'awaits its run's signature'. `read_tracked` says a damaged signed record is not the same fact as an absent one. The behaviour is fail-safe, since the learning is not carried, but the brief gives the operator the wrong reason, and a damaged signed record goes unnoticed.

## Steps to Reproduce

1. Sign a run whose listed learning goes live.
2. Corrupt the tracked record's JSON.
3. Brief the seat: the learning reads 'awaits its run's signature'.

## Proposed Fix

Have `signed_record` return a distinct damaged state, and have the brief and the close name the record as unreadable, with its path.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `run_state.signed_record` turns RunStateError into None (near line 698), so a learning whose run's tracked record cannot be parsed reads on a seat's brief as...
- [ ] **AC2** The proposed fix lands, pinned by a test: Have `signed_record` return a distinct damaged state, and have the brief and the close name the record as unreadable, with its path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
