# BG1616: lane land's several-worktree landing moves a body line shaped like a trailer into the trailers, and three of its refusals have no test

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1616.md
> **Evidence:** run eighteen, 2026-11-19: sdlc-studio/reviews/verdicts/US1192/4ee5be2fb53e-5663bc2b.txt
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:54:34Z

## Summary

Non-blocking findings from the qa review of the several-worktree land (run eighteen): a commit-message body line such as `Note: ...` is read as a trailer and moved into the trailer block, and three of the land's refusals are reached by no test.

## Steps to Reproduce

Land two worktrees whose commit-msg.txt body holds a line `Note: keep this`; the commit's trailer block carries it.

## Proposed Fix

Treat only known trailer keys, or only the final paragraph, as trailers; add a test per refusal.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings from the qa review of the several-worktree land (run eighteen): a commit-message body line such as `Note: ...` is read as a trailer and...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Land two worktrees whose commit-msg.txt body holds a line `Note: keep this`; the commit's trailer block carries it.
- [ ] **AC3** The proposed fix lands, pinned by a test: Treat only known trailer keys, or only the final paragraph, as trailers; add a test per refusal.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
