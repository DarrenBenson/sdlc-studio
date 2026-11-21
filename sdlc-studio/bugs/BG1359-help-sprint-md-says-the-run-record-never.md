# BG1359: help/sprint.md says the run record never names the plan by its .local path, but a run opened before 509850a1 still does

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, changelog.d/BG1359.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US0998-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:20:46Z

## Summary

RUN-01M77177 itself files `plan: .local/sprint-plan.json`; the sentence over-claims until such runs close (LC-018). Reported non-blocking at review.

## Steps to Reproduce

Read the sentence against the behaviour the review probed.

## Proposed Fix

Reword to what the code does.

## Acceptance Criteria

- [ ] **AC1** Given the page or output named, its wording states only what the code does. Fails on: the over-claim the review quoted.
  - **Verify:** pytest tools/tests/test_lean_docs_v63.py

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it is what is left of a fix already shipped. One pre-existing run record still files a .local plan path; new records use the digest, so the help is right for every run a user makes. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
