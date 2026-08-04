# BG0514: queue show is blind exactly when an operator uses it - it reuses the materialiser's open-run refusal

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`queue_show` delegates to `materialise_next`, which refuses first on the single-run-slot guard. So during a run - the one moment the queue exists for - `sprint queue show` reports `resolves to NOTHING runnable: run RUN-xxxx is still open` instead of what the head charter would select. The goal review line is suppressed with it, because it sits inside the same `ok` branch, so US0490's `the review travels with the charter` is invisible during a run too.

US0489 AC1 says the head's units are reported `so what will run is visible before it runs`. Verified on the live tree: with RUN-01KZ5YXM open, `queue show` resolves nothing; in a worktree with no run open the same command resolves 15 units. The criterion's verifier passes because its fixture has no open run.

The single-run-slot rule is a WRITE precondition and belongs to `next`. `queue show` is read-only inspection - showing what a charter would select cannot open anything - so reusing one function for both couples a refusal to a question that does not need it. Found by the independent batch review of RUN-01KZ5YXM.

## Steps to Reproduce

1. Open a run (`sprint plan --write ...`).
2. Run `sprint.py queue show` - the head resolves to nothing, naming the open run.
3. Close or stop the run and re-run - the same charter now resolves its units.

## Proposed Fix

Split the resolution from the open-run guard: give `queue_show` a path that resolves the head's scope without asking whether a run is open, and leave the guard where it belongs, on `next`. The refusal is right for opening and wrong for looking.

## Acceptance Criteria

- [x] `sprint queue show` reports the head charter's resolved units WITH a run open. The fixture must have a run open - that is precisely the condition US0489's passing verifier lacks, which is how the defect survived a green criterion (LL0020)
- [x] The goal-review line travels with it. Today it is suppressed because it sits inside the same `ok` branch, so US0490's "the review travels with the charter" is invisible during a run; after the fix it is visible in both states
- [x] The single-run-slot guard still refuses `next`, which WRITES. The guard moves rather than disappears, pinned by a test that runs `next` with a run open and asserts the refusal - otherwise this fix trades a blind read for an unguarded write
- [x] The mutant is the shared delegation: re-pointing `queue_show` back through `materialise_next` reddens the new test
- [x] Read-only means read-only: `queue show` with a run open writes nothing - no run state, no charter status, no queue reorder - asserted by comparing the tree before and after

## Impact

The queue's stated purpose is planning the next sprint while this one runs. The command built for that says nothing useful in exactly that state, and an operator learns to distrust it - or worse, reads `resolves to NOTHING runnable` as a fact about the charter rather than about the run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
