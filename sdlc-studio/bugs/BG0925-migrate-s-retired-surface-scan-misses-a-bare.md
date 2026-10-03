# BG0925: migrate's retired-surface scan misses a bare retired command inside a fenced code block

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/retired_surface.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_surface_fenced.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T02:49:18Z

## Summary

BG0896 (569c10e3) made a bare script name count only inside a code span, so a retired command written bare in a fenced block (a runbook's bash fence) is no longer named by migrate, where the base named it. A fenced block is code, so it should count like a span.

## Steps to Reproduce

1. A consuming README with a bash fence holding a bare retired command. 2. Run migrate's retired-surface scan. 3. The fence line is not named; at 569c10e3^ it was.

## Proposed Fix

Count a bare script name inside a fenced code block as code, as inside a span; prose stays unnamed. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a document with a bare retired command inside a fenced code block and the same name in prose, when migrate's retired-surface scan runs, then the fenced line is named and the prose line is not. Fails on: the current scan, which names neither
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_surface_fenced.py::RetiredSurfaceFencedTests::test_a_fenced_bare_command_is_named
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
