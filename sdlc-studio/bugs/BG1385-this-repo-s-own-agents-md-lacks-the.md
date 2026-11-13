# BG1385: This repo's own AGENTS.md lacks the template's 'Integrate continuously' line, so validate.py check warns here

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** AGENTS.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_own_agents_md_integration_line.py, changelog.d/BG1385.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane upgrade builder, BG1333
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:07:17Z

## Summary

After BG1333 `validate.py check` warns in this repo because AGENTS.md, held to 7,000 characters, has no line starting 'Integrate continuously'. Either AGENTS.md gains the line or the rule needs an explicit exemption for this repo.

## Steps to Reproduce

Run `python3 .claude/skills/sdlc-studio/scripts/validate.py check` in this repo.

## Proposed Fix

Add the line in under the character cap, or record the exemption.

## Acceptance Criteria

- [ ] **AC1** Given this repo's AGENTS.md, when `validate.py check` runs, then it raises no integration-rule warning and AGENTS.md stays within 7,000 characters. Fails on: the warning printed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_own_agents_md_integration_line.py::OwnAgentsMdIntegrationLineTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
