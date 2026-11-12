# BG1375: US1015's run-state floor and its Write, MultiEdit, NotebookEdit, Read and Bash evidence cases have no tests

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py, changelog.d/BG1375.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1015-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T16:24:31Z

## Summary

The In Progress floor read from the run state and the non-Edit tool cases are unpinned. Reported non-blocking at review.

## Steps to Reproduce

Apply the case the review names: see its verdict file under sdlc-studio/reviews/verdicts/US1015/.

## Proposed Fix

Handle and pin the case.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the behaviour matches the documented rule. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewTests::test_the_floor_and_each_tool_case_are_pinned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
