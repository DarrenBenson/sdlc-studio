# BG1407: A builder's mutation probe in a scratch copy of the tests runs without the repo-root conftest.py, so without HOME confinement

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_probe_home_confinement.py, changelog.d/BG1407.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane accept builder
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:34Z

## Summary

The self-check guidance does not say to copy conftest.py or run in the worktree, so a probe can touch the real HOME (BG1300's class).

## Steps to Reproduce

Run a probe in a scratch copy and check HOME.

## Proposed Fix

Add the instruction to the brief.

## Acceptance Criteria

- [ ] **AC1** Given the builder brief, when it describes a mutation probe, then it tells the builder to run in the worktree or copy conftest.py. Fails on: no such instruction.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_probe_home_confinement.py::ProbeHomeConfinementTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
