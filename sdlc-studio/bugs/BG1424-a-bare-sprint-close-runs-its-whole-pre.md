# BG1424: A bare sprint close runs its whole pre-flight report before scaffolding the retro, so the scaffold takes many minutes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_scaffold_first.py, changelog.d/BG1424.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: the run eleven close
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:49:35Z

## Summary

`sprint.py close` with no --retro computes the full owed-work pre-flight before it reaches the retro scaffold; on this repository that took over ten minutes and a first attempt was killed at 600 s with nothing scaffolded.

## Steps to Reproduce

On a large repository run `timeout 600 sprint.py close` with no --retro: it is killed before scaffolding.

## Proposed Fix

Scaffold first, then report the pre-flight; or give the scaffold its own verb.

## Acceptance Criteria

- [ ] **AC1** Given an open run with no retro, when `sprint.py close` runs with no --retro, then the retro is scaffolded before any slow pre-flight work, and the scaffold survives the process being stopped afterwards. Fails on: no retro on disk after an interrupted bare close.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_scaffold_first.py::ScaffoldFirstTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
