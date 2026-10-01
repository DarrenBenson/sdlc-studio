# BG0840: BG0818 did not converge in review: round 2 REJECT findings

> **Status:** Won't Fix
> **Closed with findings in:** D0291, discovery backlog sweep 2026-10-01 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_stage_confirm.py, .claude/skills/sdlc-studio/help/init.md, changelog.d/BG0818.md, .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T17:19:59Z

## Summary

BG0818 was rejected at round 2, the review cap, by qa-rev-a7755839, so it was carried as a known issue rather than reviewed again. The findings still open: [regression] blocking: a permission-denied AGENTS.md or prd.md crashes init guided and status hint with Errno 13 because \_read catches decode errors but not OSError; [new] non-blocking: a directory named AGENTS.md gets a directive saying it cannot be read as UTF-8; [new] non-blocking: the \_authored docstring claims more than the code-span-only exclusion; [new] non-blocking: a placeholder the template quotes only in a code span, trd.md's path token, can escape as authored

## Steps to Reproduce

1. Read the round 2 REJECT of BG0818 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0818 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0818 was rejected at round 2, the review cap, by qa-rev-a7755839, so it was carried as a known issue rather than reviewed again.
- [ ] **AC2** The proposed fix lands, pinned by a test: Fix each finding above, then deliver BG0818 again in a later run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
| 2026-09-28 | sdlc-studio v6 | Its blocking finding (an unreadable AGENTS.md or prd.md crashing init guided and status hint) is answered by BG0818's bounded round 3 (D0285, D0286). Still open: a bare {{version}} in prose holds an authored document; a placeholder a template quotes only in a code span (trd.md's path token) can escape as authored. |
