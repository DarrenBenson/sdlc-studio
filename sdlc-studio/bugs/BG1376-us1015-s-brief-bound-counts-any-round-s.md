# BG1376: US1015's brief bound counts any round's issued path, not the round being recorded

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/verdict_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py, changelog.d/BG1376.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1015-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T16:24:37Z

## Summary

A path issued for an earlier round still counts as the briefing time for a later round's self-review check. Reported non-blocking at review.

## Steps to Reproduce

Apply the case the review names: see its verdict file under sdlc-studio/reviews/verdicts/US1015/.

## Proposed Fix

Handle and pin the case.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the behaviour matches the documented rule. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewTests::test_the_bound_is_this_rounds_issued_path

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. Brief time bound counts an earlier round's path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
