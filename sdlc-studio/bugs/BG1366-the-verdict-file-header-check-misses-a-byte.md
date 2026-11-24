# BG1366: The verdict-file header check misses a byte order mark, a lower-case header or a leading prose line

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py, changelog.d/BG1366.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1013-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:21:33Z

## Summary

A file opening any of those ways is not read as carrying its header. Reported non-blocking at review.

## Steps to Reproduce

Run the case the review describes.

## Proposed Fix

Correct the behaviour and pin it.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the behaviour matches the documented rule. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py::Run10FollowUpTests

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. A BOM or lower-case header; workaround is to write the header as documented.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
