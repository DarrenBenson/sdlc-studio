# BG1381: A price source URL whose path ends in a closing bracket loses that bracket from its link target

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py, changelog.d/BG1381.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-BG1374-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T16:50:17Z

## Summary

BG1374's address match stops before a final ')', so a link to such a page points at the wrong address. Reported non-blocking at review.

## Steps to Reproduce

Render the case the review names into the Markdown twin.

## Proposed Fix

Handle and pin the case.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the twin renders it as documented. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_pricing_snapshot.py::PricingSnapshotTests::test_a_closing_bracket_in_a_url_path_is_kept

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it needs a condition no real install meets. No shipped price source URL ends in a closing bracket; the defect needs a hand-written source. Link target only in the Markdown twin. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
