# BG1348: critic.py's 'none blocking' guard has no test

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py, changelog.d/BG1348.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-BG1030-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:42Z

## Summary

The guard at critic.py:3645 that reads BLOCKING as none when it opens with 'none' is unpinned; a mutant of it survives. Reported non-blocking at review.

## Steps to Reproduce

Apply the surviving mutant the review names: the suite stays green.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given the behaviour named, a test fails when it is broken. Fails on: the surviving mutant the review named.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_trailing_prose.py::TrailingProseTests::test_the_none_blocking_guard_is_pinned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
