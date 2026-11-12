# BG1373: A NUL byte in a transcript's file path makes critic.py record refuse the unit

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/verdict_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py, changelog.d/BG1373.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1015-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:22:13Z

## Summary

US1015's self-review check reads Edit paths from the session's transcripts; a path holding a NUL byte raises and record refuses the unit instead of skipping that record. Reported non-blocking at review.

## Steps to Reproduce

Apply the case the review names: see its verdict file under sdlc-studio/reviews/verdicts/US1015/.

## Proposed Fix

Handle and pin the case.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the behaviour matches the documented rule. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_review_by_context.py::SelfReviewTests::test_a_nul_path_in_a_transcript_is_skipped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
