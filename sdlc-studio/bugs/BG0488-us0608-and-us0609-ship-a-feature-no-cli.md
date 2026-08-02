# BG0488: US0608 and US0609 ship a feature no CLI invocation can reach, and their tests survive its deletion

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Severity:** High
> **Points:** 5

## Summary

EP0200 decouples a stale periodic review from the close. An independent pass showed the delivered pair is inert and unpinned.

US0608: reverting the whole feature - `"blocking": False` back to `True` at gate.py:1397 - SURVIVES all 390 tests of `test_gate.py.` That is the mutant AC1's own docstring names. All four ACs call the private `_batch_is_independently_covered` or grep source text; none asserts the lane's blocking flag and none runs a close, though AC1 says 'When the close runs / Then it proceeds'.

US0609: `_is_cadence_debt` has one call site, and the marker it looks for is produced in exactly one place - gate.py:1398 - which sets `"blocking": False`. `close_preflight` only raises a blocker when `status=="fail" and c.get("blocking")`. Executed on the real repo with the batch forced covered: 25 blockers returned, ZERO carrying the marker. US0608, same epic, converts the blocker to non-blocking before US0609 can ever see it. Deleting `and not _is_cadence_debt(b)` survives all 701 tests of `test_sprint.py.`

The implementations are individually correct - forcing coverage does make `review-current` report status=fail, blocking=False. The wiring between them is what nobody exercised.

## Steps to Reproduce

1. In a worktree, set `"blocking": True` at gate.py:1397. Run `test_gate.py` -> 390 passed.
2. Delete `and not _is_cadence_debt(b)` from sprint.py:6232. Run `test_sprint.py` -> 701 passed.
3. Force the batch covered and call `close_preflight` on the real repo; count blockers carrying the CADENCE DEBT marker -> 0 of 25.

## Proposed Fix

Decide first whether the pair is coherent: if US0608 makes the lane non-blocking, US0609's filing path may be dead by construction rather than by defect, in which case one of the two should be withdrawn rather than repaired. Then pin whichever survives on the CLI - a close that runs, and the close-owed ledger read - not on a private helper or a source grep.

## Impact

Two units of a three-unit epic are recorded delivered on evidence that cannot fail. The cadence-debt path they exist to provide cannot be produced by any command, so the bounded exit the epic promised is not available. This is the same defect class `verify_ac lane-check` was shipped for in the adjacent epic, and it flagged both.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
