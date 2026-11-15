# BG1450: A reviewer's verdict file is refused by critic.py record over one code span with a leading space, and the review brief does not warn

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_brief_code_span_warning.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1450.md
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:38:02Z

## Summary

US0995's verdict held a code span whose text began with a space (the tier followed by (explicit)); `critic.py record` refused it (markdownlint MD038 would refuse the ledger), so the reviewer had to be resumed to rewrite its own file. The brief's verdict format section says nothing about it.

## Steps to Reproduce

Write a verdict whose ISSUES hold a code span starting with a space, then record it: refused.

## Proposed Fix

Say in the brief's verdict-format text that a code span must not start or end with a space, or have record pad such a span safely.

## Acceptance Criteria

- [ ] **AC1** Given a review brief, when a reviewer reads its verdict format, then it states the code-span rule. Fails on: no mention.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_code_span_warning.py::BriefCodeSpanWarningTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
