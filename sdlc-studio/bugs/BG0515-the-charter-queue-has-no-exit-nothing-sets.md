# BG0515: the charter queue has no exit - nothing sets Spent, and next never opens a run

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`Spent` is declared in `lib/sdlc_md.py` as the charter's successful terminal and ships in the versioned schema contract at `reference-schema.md`. No code path sets it. `grep -rn Spent scripts/ | grep -v test_` finds the declaration and nothing else.

The cause is that `sprint next` RESOLVES and reports rather than opening a run: opening is `sprint plan --write`, which knows nothing about charters, so nothing ever marks the charter it came from as spent. A charter therefore stays Queued forever and re-materialises at the head of every subsequent `next`.

US0488's criteria are all about resolution and refusal and all hold, so this is not a defect against that unit - it is the seam between resolving a charter and opening its run, which no unit in EP0176 owns. Found by the independent batch review of RUN-01KZ5YXM, which also noted the `--dry-run` flag had no distinct behaviour for the same reason (both branches wrote nothing); that half is repaired.

## Steps to Reproduce

1. Queue a charter with a resolvable scope query.
2. `sprint.py next` - it reports the resolved units.
3. `sprint.py plan --worklist <those ids> --write` - the run opens.
4. Read the charter: still `Queued`. `sprint.py queue show` still names it as the head.

## Proposed Fix

Decide where the charter is spent and make one place do it. Either `next` opens the run itself and marks the charter Spent in the same act, or `plan --write` accepts the charter id it is materialising from and marks it. The first keeps the charter lifecycle in one command; the second keeps run-opening in one command. Whichever is chosen, the queue needs an exit or it is not a queue.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `Spent` is declared in `lib/sdlc_md.py` as the charter's successful terminal and ships in the versioned schema contract at `reference-schema.md`.
- [ ] The proposed fix lands, pinned by a test: Decide where the charter is spent and make one place do it.

## Impact

A charter is never consumed, so the queue never advances: every `next` returns the same head, and an operator who has run that charter has no way to say so except by cancelling it - which records a withdrawal, a different and misleading fact.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
