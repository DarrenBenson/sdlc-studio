# BG1415: No test pins the line number verify_ac's lint prints

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_section_boundary.py, .claude/skills/sdlc-studio/scripts/tests/test_lint_line_number.py, changelog.d/BG1415.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: process section, BG0991 review
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:13:34Z

## Summary

BG0991's lint output names a line, which no test checks.

## Steps to Reproduce

Lint a Verify line on a known line.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given a lint failure, when printed, then the line number is the right one. Fails on: a wrong line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lint_line_number.py::LintLineNumberTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
