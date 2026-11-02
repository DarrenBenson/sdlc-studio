# BG1182: `test_agents_md_full_suite_rule`'s `_problems` docstring says it lists every way the text falls short of AC1, but it checks more than AC1 and stops early

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_agents_md_full_suite_rule.py, changelog.d/BG1182.md
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:07:06Z

## Summary

Found by US1090's author self-check (2026-11-02). The docstring says 'Every way `text` ... falls short of AC1; empty when it meets it.' Appending a sentence naming `sdlc.gateHostName` meets all three AC1 conditions, yet `_problems` reports that key, because its key and path checks go beyond AC1. It also returns early when the rule leads two paragraphs, so the span checks are skipped.

## Steps to Reproduce

1. Append '`sdlc.gateHostName`' to the rule's paragraph in a scratch AGENTS.md.
2. Call `_problems`: one problem, though AC1 is met.

## Proposed Fix

Reword the docstring to say what the function checks: AC1 plus the key and path checks, and the early return.

## Acceptance Criteria

- [ ] **AC1** `_problems`'s docstring names the key and path checks and the early return.
  - **Verify:** pytest tools/tests/test_agents_md_full_suite_rule.py

## Impact

A reader of the test trusts a docstring that over-states its scope.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
