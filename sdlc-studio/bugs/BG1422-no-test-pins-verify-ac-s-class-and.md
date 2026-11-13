# BG1422: No test pins verify_ac's class and module skip-mark check on the decorator's name

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py, changelog.d/BG1422.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: qa-seat-BG1005-r1 round 2
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:49:21Z

## Summary

The repair for the class and module skip shape matches a skip mark by its reason and the decorator; no test fails if the decorator-name check is dropped, so a non-skip decorator with the same reason text could be named as the skip.

## Steps to Reproduce

Drop the decorator-name check in `_skip_marked_class` and run `test_verify_ac_partial_skip.py`: it stays green.

## Proposed Fix

Add a fixture class with a lookalike decorator and assert it is not named.

## Acceptance Criteria

- [ ] **AC1** Given a class carrying a non-skip decorator whose argument matches a skipped test's reason, when `verify_ac` names the skip, then it does not name that class. Fails on: the class named.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_partial_skip.py::SkipMarkDecoratorNameTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
