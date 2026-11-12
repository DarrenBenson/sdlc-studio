# BG1371: The retro's dollar line prices only the meter's split, so the retro and the report state different dollars for one run

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, changelog.d/BG1371.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1000-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:22:02Z

## Summary

retro.py's `_usd_batch` (retro.py:1668) leaves out the delegated totals the report now prices (US1000). Reported non-blocking at review.

## Steps to Reproduce

Run the case the review describes.

## Proposed Fix

Correct the behaviour and pin it.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, the behaviour matches the documented rule. Fails on: the case as the review probed it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::Run10FollowUpTests
  - **Verified:** yes (2026-11-12)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
