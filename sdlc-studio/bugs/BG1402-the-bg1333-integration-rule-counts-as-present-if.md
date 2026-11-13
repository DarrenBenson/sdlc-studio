# BG1402: The BG1333 integration rule counts as present if 'Integrate continuously' appears anywhere in AGENTS.md, so a sentence negating it passes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_integration_rule_negation.py, changelog.d/BG1402.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review upgrade, BG1333
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:56Z

## Summary

validate.py:1072 matches the lead phrase anywhere, so 'Never integrate continuously' satisfies it.

## Steps to Reproduce

Write 'We do not Integrate continuously' in AGENTS.md.

## Proposed Fix

Anchor the phrase to a line start.

## Acceptance Criteria

- [ ] **AC1** Given an AGENTS.md whose only mention negates the rule, when validate runs, then it warns. Fails on: the negation passing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_integration_rule_negation.py::IntegrationRuleNegationTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
