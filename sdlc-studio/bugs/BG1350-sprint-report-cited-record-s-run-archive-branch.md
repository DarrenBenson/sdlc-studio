# BG1350: sprint_report._cited_record's run-archive branch has no test

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py, changelog.d/BG1350.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US0997-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:55Z

## Summary

The branch citing a run archive is unpinned; mutant M7 survives. Reported non-blocking at review.

## Steps to Reproduce

Apply the surviving mutant the review names: the suite stays green.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given the behaviour named, a test fails when it is broken. Fails on: the surviving mutant the review named.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_cites_committed_record.py::CitedRecordTests::test_the_run_archive_branch_is_pinned

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. _cited_record's run-archive branch behaves correctly; mutant M7 survives for want of a test. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
