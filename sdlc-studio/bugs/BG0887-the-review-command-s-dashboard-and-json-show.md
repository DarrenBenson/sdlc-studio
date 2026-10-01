# BG0887: The review command's dashboard and JSON show a per-document health percentage that no code computes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/review.md
> **Evidence:** US0973 QA review round 2 (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T19:02:08Z

## Summary

reference-review.md:357-372 and 624 render a PRD REVIEW bar at 85%, reference-review.md:796-801 a JSON with `overall_health` and health keys, and help/review.md:92 and 99 the same; nothing defines how the percentage is derived, the gap US0973 closed for status.

## Steps to Reproduce

1. Read reference-review.md:357-372 and :796-801. 2. grep the scripts for `overall_health` - nothing computes it.

## Proposed Fix

Drop the per-document percentages, or show the counts the review actually produces, as US0973 did for status.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: reference-review.md:357-372 and 624 render a PRD REVIEW bar at 85%, reference-review.md:796-801 a JSON with `overall_health` and health keys, and...
- [ ] **AC2** The proposed fix lands, pinned by a test: Drop the per-document percentages, or show the counts the review actually produces, as US0973 did for status.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
