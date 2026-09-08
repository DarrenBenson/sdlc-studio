# CR-0568: mutation.py register replaces a live row with the same unit, criterion, row, target and hash instead of appending a duplicate

> **Status:** Complete
> **Decomposed-into:** EP0249
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** RUN-01M1WPNV delivery, 2026-09-07: BG0646 (two REJECTs r1) and BG0649 (three REJECTs r1, two r2) - every rejection was a check a seat did in minutes that the author had not: run the shipped lane on this repository, measure a number written into prose, write a mutant for a branch the fixture never reached. Analysis recorded in the run's retro.
> **Date:** 2026-09-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Re-running a registration runner after another target changed appended duplicate rows for the unchanged targets; the author patched the runner to skip rows already live, which is the tool's job. A duplicate live row makes the stale row win the (criterion, row) join (memory: mutation-ledger-duplicate-rows) and inflates the executed count. `register` should replace the live row with the same key on the same hash, and say so.

## Impact

The ledger's executed and killed counts stop inflating on a re-registration, and the (criterion, row) join reads the current row rather than a stale duplicate.

## Acceptance Criteria

- [ ] Given a live row for (unit, criterion, row) on a target's current hash, when the same registration is made again, then the ledger holds one row for the key and the command reports the replacement; a registration for a different row still appends - the control.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Raised |
