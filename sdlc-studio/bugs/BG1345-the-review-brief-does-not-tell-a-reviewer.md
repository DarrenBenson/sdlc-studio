# BG1345: The review brief does not tell a reviewer to keep tools that write under the home directory, such as npx and npm, out of its probes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1345.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1011-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:24Z

## Summary

A QA reviewer ran `npx markdownlint`, which wrote npm debug logs under the operator's real ~/.cache/npm/_logs/. The brief says to probe in a scratch copy but says nothing about tools whose own state lives under the home directory.

## Steps to Reproduce

Review a unit whose docs a reviewer wants to lint: it runs npx.

## Proposed Fix

Add the line to the brief's probing rule.

## Acceptance Criteria

- [ ] **AC1** Given any review brief, when it is printed, then its probing rule names tools that write under the home directory (npx, npm) as off limits or to be run with a temporary HOME. Fails on: a brief silent on them.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefSafetyTests::test_the_brief_keeps_home_writing_tools_out_of_probes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
