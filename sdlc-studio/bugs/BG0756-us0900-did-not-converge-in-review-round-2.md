# BG0756: US0900 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0900 was rejected at round 2, the review cap, by qa-rev-US0900, so it was carried as a known issue rather than reviewed again. The findings still open: [new] the v3 creator and validator still disagree: a minimal CR validates at inbox and Proposed but fails evidence-present once triaged to Approved, refined to In Progress or rejected, because no tool ever writes a Size or Impact onto the CR - the refusal moved again rather than retiring [LC-008]; [new] help/cr.md, the changelog and file\_finding.py say refine gives the CR its size, which is false: refine sizes the epic [LC-004]; [new] non-blocking: US0128 AC2 retired and AC3 honest (closed); [new] non-blocking: prose Affects and the Impact placeholder (closed)

## Steps to Reproduce

1. Read the round 2 REJECT of US0900 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0900 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0900 was rejected at round 2, the review cap, by qa-rev-US0900, so it was carried as a known issue rather than reviewed again.
- [ ] **AC2** The proposed fix lands, pinned by a test: Fix each finding above, then deliver US0900 again in a later run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
