# BG0761: US0904 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Carried work:** the round-2 patch is kept at sdlc-studio/.local/US0904-carried-r2.patch, complete against 25cbd375 and passing every other probe. Remaining fix: in sprint_report.classify_refusals change `when > at` to `when >= at` (git stamps a commit when it starts, before its hooks) and add a fixture row whose retry carries the refusal's own second; then add the message-refusal test to AC1's Verify line and reword AC2 to the blob rule
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, tools/tests/test_lean_refusal_log.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py, changelog.d/US0904.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0904 was rejected at round 2, the review cap, by qa-rev-US0904, so it was carried as a known issue rather than reviewed again. The findings still open: [new] classify\_refusals joins by committer time strictly after the refusal, but git stamps a commit when it starts, so a same-second retry reads pending: fix is when >= at plus a same-second fixture row [LC-002]; [new] non-blocking: git log --raw without -z quotes non-ASCII paths so they misclassify; [new] non-blocking: commit-msg blob recording unpinned [LC-002]; [new] non-blocking: AC2 text still says any code change is a catch while the pinned rule is blob-based; [new] non-blocking: AC1 Verify line omits the message-refusal test [LC-002]; [new] non-blocking: a missing log means both no-refusal-yet and consuming project [LC-006]

## Steps to Reproduce

1. Read the round 2 REJECT of US0904 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0904 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0904 was rejected at round 2, the review cap, by qa-rev-US0904, so it was carried as a known issue rather than reviewed again.
- [ ] **AC2** The proposed fix lands, pinned by a test: Fix each finding above, then deliver US0904 again in a later run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
