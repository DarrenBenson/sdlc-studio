# BG0686: BG0493 AC2's test reads a fixture hook, so deleting the real pre-commit hook's lane-check block survives

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .githooks/pre-commit
> **Evidence:** RUN-01M2JA6J evidence-drift re-verification, 2026-09-15: survived on HEAD 6fd766cc and on the working tree.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0493 AC2 pins that the lane-check guard runs in the tracked pre-commit hook. Its test was rewritten on 2026-09-10 to run against a fixture hook and no longer reads .githooks/pre-commit, so the planned mutant (delete the real hook's lane-check comment block and call) survives on HEAD. The ledger's killed row predated the rewrite; re-measured 2026-09-15 it survives and is now recorded as survived. The other AC2 kill, on `test_gate.py`, was already stale, so AC2 has no live kill.

## Steps to Reproduce

1. Delete the '# lane-check:' block in .githooks/pre-commit.
2. Run pytest .claude/skills/sdlc-studio/scripts/tests/`test_gate.py`::LaneCheck... (BG0493 AC2's selector).
3. It passes.

## Proposed Fix

Point AC2's test at the tracked hook's text (or run the tracked hook in a fixture repo) so removing the real lane fails it; re-register the row killed.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0493 AC2 pins that the lane-check guard runs in the tracked pre-commit hook.
- [ ] **AC2** The proposed fix lands, pinned by a test: Point AC2's test at the tracked hook's text (or run the tracked hook in a fixture repo) so removing the real lane fails it; re-register the row killed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - lane-check pre-commit block test: D0260/US0879 removed lane-check from pre-commit |
