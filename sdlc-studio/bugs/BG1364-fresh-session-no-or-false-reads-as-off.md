# BG1364: fresh_session: no or false reads as off, though the help and US1149's AC2 say any other value reads as warn

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py, changelog.d/BG1364.md, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1149-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:21:20Z

## Summary

YAML false from a bare no or false maps to off. Reported non-blocking at review.

## Steps to Reproduce

Run the case the review describes.

## Proposed Fix

Correct the behaviour and pin it.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the behaviour matches the documented rule. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py::Run10FollowUpTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
