# BG1171: reconcile settle closes an epic in the pre-commit hook but leaves the requests that close made derivable, so the same commit's gate refuses on that drift

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, changelog.d/BG1171.md
> **Evidence:** The pre-commit log of the US1102/BG1166 closing commit, 2026-11-01: 'settle settled EP0293: Draft -> Done', then '[FAIL] reconcile [9.0s]: 4 drift item(s)'.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T09:23:47Z

## Summary

2026-11-01, run four. The commit that closed US1102, the last story of EP0293, ran `reconcile.py settle` in the pre-commit hook. Settle set EP0293 Draft to Done and restaged it. The same hook's gate lane then failed on 4 drift items: 'request-derivable CR0645/CR0646/CR0647/CR0649: ... every child it produced is resolved - its terminal is DERIVED, so `reconcile apply` sets it Complete'. Settle's help says it fixes 'the mechanical drift a commit would otherwise refuse (indexes, derived epic closes)'. Its own epic close creates request-derivable drift that it leaves for a second command and a second commit attempt.

## Steps to Reproduce

1. Close the last open story of an epic that a CR produced.
2. Commit: settle closes the epic, and the gate lane refuses on request-derivable drift.
3. Run `reconcile.py apply` and commit again: green.

## Proposed Fix

After settle derives an epic close, have it derive the request terminals that close made earnable, as `reconcile apply` does, then restage them.

## Acceptance Criteria

- [ ] **AC1** A commit whose settle closes a request's last epic also derives that request's terminal and passes the gate's reconcile lane in one attempt.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py

## Impact

Every commit that closes a CR's last epic is refused once, and costs a second hook run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
