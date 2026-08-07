# BG0542: sprint plan under affects_check: block prints REFUSED, exits 0, and writes the unit into the batch - worse than the honest advisory it replaced

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, independent delivery review of BG0521. `git log -S 'REFUSED under sprint.affects_check'` returns only the repair commit, so the false wording is this run's, not pre-existing.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0521 was filed because `plan` under `block` was byte-identical to `warn`. Its repair made the message say REFUSED. It did not make the command refuse.

Probed through the shipped CLI on a throwaway fixture: `sprint plan --worklist ... --write` under `sprint.affects_check: block` prints `Affects contradicted by the unit's own content - REFUSED under sprint.affects_check: block:`, exits 0, and writes the offending unit into the batch.

That is worse than the state it replaced. At the run's base ref the same path said `advisory - nothing is refused`, which was true. The repair replaced a true statement with a false one, and the word REFUSED is precisely the refusal-that-is-a-message this bug was filed to remove.

## Steps to Reproduce

1. Set `sprint.affects_check: block` in a fixture project. 2. Give a unit an Affects its own content contradicts. 3. `sprint plan --worklist <unit> --write`. 4. The output says REFUSED, the exit code is 0, and the batch contains the unit.

## Proposed Fix

Return non-zero and write nothing on the block path, which is what the word means and what the criterion says. The four criterion-level mutants all die on a clean tree, so the unit's tests are sound - they simply never assert the exit code or the batch contents through the command, which is where the behaviour lives.

Also: the CHANGELOG claims all three call sites ask one reader, `_affects_blocking`. `cmd_batch` calls `affects_check_mode(root)` directly, so only two of the three do.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0521 was filed because `plan` under `block` was byte-identical to `warn`.
- [ ] **AC2** The proposed fix lands, pinned by a test: Return non-zero and write nothing on the block path, which is what the word means and what the criterion says.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
