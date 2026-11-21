# BG1351: US1149's tests have no fixture with two synthetic records in a row

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py, changelog.d/BG1351.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1149-r1 round 2
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:20:01Z

## Summary

A mutant that skips only the last synthetic record survives, because no fixture ends in two. Reported non-blocking at review.

## Steps to Reproduce

Apply the surviving mutant the review names: the suite stays green.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given the behaviour named, a test fails when it is broken. Fails on: the surviving mutant the review named.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::FreshSessionTests::test_two_trailing_synthetic_records_are_skipped

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. US1149's behaviour is right; only a fixture ending in two synthetic records is missing. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
