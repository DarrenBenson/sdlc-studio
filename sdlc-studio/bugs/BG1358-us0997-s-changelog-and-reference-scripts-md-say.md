# BG1358: US0997's changelog and reference-scripts.md say the close commits the run record, but it files it

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-scripts.md, changelog.d/BG1358.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US0997-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:20:40Z

## Summary

changelog.d/US0997.md and reference-scripts.md over-claim. Reported non-blocking at review.

## Steps to Reproduce

Read the sentence against the behaviour the review probed.

## Proposed Fix

Reword to what the code does.

## Acceptance Criteria

- [ ] **AC1** Given the page or output named, its wording states only what the code does. Fails on: the over-claim the review quoted.
  - **Verify:** pytest tools/tests/test_lean_docs_v63.py

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. Changelog says commits where it files.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
