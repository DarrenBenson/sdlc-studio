# BG1653: BG1002's _live_run comment claims a missing run state is handled, and four branches of the live-run read have no test

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_live_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:32:58Z

## Summary

BG1002's engineering second seat (verdict sdlc-studio/reviews/verdicts/BG1002/c0b12eefb2b4-93088a11.txt, RUN-01M7VNR0): sprint.py's `_live_run` comment says it handles a missing run state, but it only catches an unreadable file, which the code before a011a415 already ignored; four branches of the fix are unpinned.

The qa seat (verdict `sdlc-studio/reviews/verdicts/BG1002/0a053133c4a3-3c7fea6a.txt`) found two more: the goal brief silently drops a declared `--serves` value nothing on disk names (after `plan --write --serves "Nobody Here"` the brief says Goal serves: NONE and never mentions the declaration, though `goal_trace` returns it in `unknown`); and the absent-value rule for `sprint_serves` (`sprint.py`:12135-12141) is unpinned, so a re-plan without `--serves` could erase the declaration with the suite green.

## Steps to Reproduce

Read `_live_run` in sprint.py at a011a415 against its comment; mutate each of the four branches the verdict names and run tests/`test_goal_review_brief_live_state.py`: green.

## Proposed Fix

Make the comment say what the code catches, and add a test per branch.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1002's engineering second seat (verdict sdlc-studio/reviews/verdicts/BG1002/c0b12eefb2b4-93088a11.txt, RUN-01M7VNR0): sprint.py's `_live_run` comment says it...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read `_live_run` in sprint.py at a011a415 against its comment; mutate each of the four branches the verdict names and run...
- [ ] **AC3** The proposed fix lands, pinned by a test: Make the comment say what the code catches, and add a test per branch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
