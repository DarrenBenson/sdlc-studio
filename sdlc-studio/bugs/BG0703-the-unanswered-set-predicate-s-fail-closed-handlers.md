# BG0703: The unanswered-set predicate's fail-closed handlers and the handoff behaviours around it survive mutants no test kills

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0626-delivery-qa.txt (qa seat); verdicts/US0626-delivery-qa-r2.txt (qa seat, round two); verdicts/US0626-delivery-engineering.txt (engineering seat); verdicts/US0626-delivery-engineering-r2.txt (engineering seat, round two); verdicts/US0823-delivery-qa.txt (qa seat); verdicts/US0823-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Each of these mutants survives the 46 US0626 tests, though each branch refuses correctly when run alone today: the fail-closed handlers in `_close_checklist` (sprint.py:5997), `_checklist_blockers` (7626) and `cmd_stop` (10669) made pass-through; the preflight calling `unanswered_units` without `retro_id` (7625), which then holds a unit the chain step passes; the hold line dropped from the stop-ship and mutation-mode branches (6013, 6021); stop's ways-out line removed (10682); the run id matched as a bare substring (5792); rung end compared without the type vocabulary (5889); status read raw (5851); and 'not abandoned' dropped from rejected (5870), which changes only the why text. The evidence limb is restated in `unanswered_units` (5877-5879) beside `_awaits_signoff`'s own copy (10551-10553), two copies that must move together. For the routes built on the predicate, each of these left `test_sprint`, `test_handoff` and `test_handoff_line` green: dropping generate's retro pass-through (handoff.py:790), which makes generate --retro RETRO0001 read a newer RETRO0002; rendering a failed predicate as none (handoff.py:503), which makes the handoff say 'None: every batch unit is delivered...' after the predicate raised; recording a failure as an empty list instead of null (sprint.py:5931); and removing the stop --force waived line (sprint.py:10703) or the pickup note (handoff.py:702). The changelog claims each of these behaviours.

## Steps to Reproduce

Apply any listed mutant in a throwaway copy - for example replace the body of the fail-closed except in `_close_checklist` with pass, or make handoff.build render a raised predicate as an empty set - and run `test_sprint.py`, `test_handoff.py` and `test_handoff_line.py`: green.

## Proposed Fix

Add a test per branch, driven through the CLI where the behaviour is a printed line, and share one evidence-limb helper between `unanswered_units` and `_awaits_signoff.`

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Each of these mutants survives the 46 US0626 tests, though each branch refuses correctly when run alone today: the fail-closed handlers in `_close_checklist`...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Apply any listed mutant in a throwaway copy - for example replace the body of the fail-closed except in `_close_checklist` with pass, or make handoff.build...
- [ ] **AC3** The proposed fix lands, pinned by a test: Add a test per branch, driven through the CLI where the behaviour is a printed line, and share one evidence-limb helper between `unanswered_units` and...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
