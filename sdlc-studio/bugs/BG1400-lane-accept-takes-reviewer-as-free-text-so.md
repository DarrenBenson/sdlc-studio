# BG1400: lane accept takes --reviewer as free text, so a carried unit's re-review under the wrong id strands an APPROVE that only an operator supersession retires

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_carried_reviewer_id.py, changelog.d/BG1400.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: review reaper
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:39Z

## Summary

A carried unit's re-review must be recorded under the id that rejected it (qa-seat-<unit>-r1). `lane accept` (lanes.py:565, sprint.py:12982) neither says nor defaults to it.

## Steps to Reproduce

Accept a re-review under another reviewer id.

## Proposed Fix

Default the id from the carried row and refuse a mismatch.

## Acceptance Criteria

- [ ] **AC1** Given a carried unit, when `lane accept` runs without a matching --reviewer, then it defaults to or names the required id. Fails on: an APPROVE stranded under a wrong id.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_carried_reviewer_id.py::CarriedReviewerIdTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
