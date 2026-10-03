# BG0887: The review command's dashboard and JSON show a per-document health percentage that no code computes

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/review.md, tools/tests/test_lean_review_health_docs.py, changelog.d/BG0887.md
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

- [ ] **AC1** Given `reference-review.md` and `help/review.md`, when their dashboard and JSON samples are read, then no per-document review bar carries a percentage and no `overall_health` or `health` key appears; each document section shows the finding counts the review produces. A measured coverage figure against its target is not a health score and may stay.
  - **Verify:** pytest tools/tests/test_lean_review_health_docs.py::ReviewHealthDocsTests::test_no_document_health_percentage_is_shown
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD's `PRD REVIEW ... 85%` bars and the JSON's `"overall_health": 85`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 78ae6c43: reference-review.md:357-371 and :624 render per-document REVIEW bars at 85/92/78/95%, :796-801 a JSON with `overall_health` and `health` keys, help/review.md:92-99 the same bars; no script computes `overall_health` or a document health; criteria authored, Points and Affects set |
