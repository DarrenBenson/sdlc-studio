# BG1155: decisions.read_once's change detection is pinned only by a growing file: dropping inode, mtime or ctime from its identity stays green

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate_reads_once.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, BG1109 APPROVE by qa-seat-BG1109-r1 (brief 2a598c381e45).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T05:02:06Z

## Summary

qa-seat-BG1109-r1's APPROVE of BG1109 (2026-11-01) found two mutants that survive all 7 tests in `test_gate_reads_once.py`: an identity of size alone, and the identity without `st_ctime_ns` (decisions.py:140). Every change in the fixtures appends a row, so the file always grows and size alone tells the versions apart. The code is right: a probe rewrote a settled, memoised ledger in place at the same size, kept its inode, restored its mtime with os.utime, and the ledger was re-read, with only ctime telling the two apart. But no test pins the inode, mtime or ctime parts, so a later edit that narrows the identity stays green.

## Steps to Reproduce

1. In a throwaway worktree set `ident = (st.st_size,)` at decisions.py:140.
2. Run `test_gate_reads_once.py`: 7 passed.

## Proposed Fix

Add a fixture that rewrites a memoised ledger in place at the same size, with mtime restored, and asserts the second read sees the new content; and one for a same-inode same-size rewrite within the racy window.

## Acceptance Criteria

- [ ] **AC1** A same-size in-place rewrite of a memoised ledger, with its mtime restored, is re-read, and the size-only and no-ctime identity mutants each fail a test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_reads_once.py

## Impact

A narrowed memo identity would serve a stale ledger to the gate after a same-size rewrite, with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
