# BG1360: reference-scripts-review.md says row_identity digests the first eight cells, but in a nine-cell row it digests every cell except Source

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-scripts-review.md, changelog.d/BG1360.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1012-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:20:53Z

## Summary

reference-scripts-review.md:127 and changelog.d/US1012.md are stale since US1012. Reported non-blocking at review.

## Steps to Reproduce

Read the sentence against the behaviour the review probed.

## Proposed Fix

Reword to what the code does.

## Acceptance Criteria

- [ ] **AC1** Given the page or output named, its wording states only what the code does. Fails on: the over-claim the review quoted.
  - **Verify:** pytest tools/tests/test_lean_docs_v63.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
