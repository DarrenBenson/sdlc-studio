# BG0702: The unanswered set's ways out are picked by substring and offer dead ends for a stop-ship ruling, and the set is rendered and recorded in drifting copies

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0626-delivery-engineering.txt (engineering seat); verdicts/US0626-delivery-engineering-r2.txt (engineering seat, round two); verdicts/US0626-delivery-qa-r2.txt (qa seat, round two); verdicts/US0823-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`unanswered_ways_out` picks remedies by substring over the joined why text, and 'ruling unreadable' is a bare literal beside the `WHY_` constants (sprint.py:5939, 5953). Its stop-ship case is now wrong: for a Done or dropped unit ruled stop-ship it offers 'finish it' and 'batch drop', which answer nothing since the repair (sprint.py:5956-5958), and never names revising the ruling. The close preflight reports a stop-ship-ruled batch unit twice, once in the stop-ship rows (sprint.py:7594-7599) and again in the hold line (7632-7635), so `preflight_headline` counts one fact as two blockers. `handoff._unanswered_body` re-implements the row format of `sprint.unanswered_rows`, which the same change added as the one shared row shape (handoff.py:673-675 against sprint.py:5910). A successful `unanswered_record` write carries no `unanswered_error` key and `run_state.update` merges fields, so a set written once on failure and again on success (the boundary's already-closed branch re-writes after generate --outcome) keeps a stale `unanswered_error` beside a valid list (sprint.py:5925-5933).

## Steps to Reproduce

1. Rule a Done batch unit stop-ship in the run's retro and run python3 .claude/skills/sdlc-studio/scripts/sprint.py stop - the ways-out line offers 'finish it' and 'batch drop' and does not mention revising the ruling. 2. sprint.py preflight on the same state - the unit is listed twice and counted as two blockers. 3. Record the set once with the predicate raising, then once succeeding - the archived record holds both `unanswered_error` and the list.

## Proposed Fix

Key remedies on the `WHY_` constants, not substrings, and add a constant for an unreadable ruling. For a stop-ship ruling, name revising the ruling as the way out. Count a unit once in the preflight. Render handoff rows through `unanswered_rows.` Write `unanswered_error` as null on a successful write.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `unanswered_ways_out` picks remedies by substring over the joined why text, and 'ruling unreadable' is a bare literal beside the `WHY_` constants...
- [ ] **AC2** The proposed fix lands, pinned by a test: Key remedies on the `WHY_` constants, not substrings, and add a constant for an unreadable ruling.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
