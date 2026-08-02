# BG0502: a close sealed by --file-and-close tells the operator nothing, because cmd_close returns before the report

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Found by the round-four independent pass on US0604 during the RUN-01KYZKY5 close, reproduced live in a fixture.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** closing review RUN-01KYZKY5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The close report is emitted from two places: `cmd_close`'s success path and the --apply-signoff tail. The --file-and-close route returns before both, so a run sealed `closed-outstanding` prints no CLOSE REPORT at all. That is the route taken when a close is BLOCKED and its ceremony debt is filed and deferred, which is precisely the case where the operator most needs an account of what shipped, what is carried and what was deferred.

## Steps to Reproduce

Drive a close whose blockers are all deferrable to `sprint.py close --file-and-close --retro RETROxxxx` and read stdout: the filing summary appears, no CLOSE REPORT does.

## Proposed Fix

Emit the report on that route too, before the bounded-exit return, and pin it with a criterion driven through the command. Decide whether a `closed-outstanding` report should name the deferrals in its own section.

## Acceptance Criteria

- [ ] A close sealed with --file-and-close prints the close report, naming what was deferred, and a test driven through the command reddens if the call is removed.

## Impact

The one exit designed for a close that could not complete cleanly is the one that reports least.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | closing review RUN-01KYZKY5 | Filed |
