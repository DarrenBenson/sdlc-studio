# BG1450: A reviewer's verdict file is refused by critic.py record over one code span with a leading space, and the review brief does not warn

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_brief_code_span_warning.py, changelog.d/BG1450.md
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log. Reproduced at cecc9dfe: a first-round brief's return contract (`_RETURN_CONTRACT`) says nothing about whitespace at a code span's edge, 2026-11-24.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:38:02Z

## Summary

US0995's verdict held a code span whose text began with a space (the tier followed by (explicit)); `critic.py record` refused it (markdownlint MD038 would refuse the ledger), so the reviewer had to be resumed to rewrite its own file. The brief's return contract (`_RETURN_CONTRACT` in critic.py, printed in every first-round and rejoinder brief) says how to tag and separate findings but nothing about it. Padding is no way out: `_clean` already explains that CommonMark strips one space from each side of a padded span, so record cannot keep such a value in a span, and the refusal stays.

## Steps to Reproduce

1. `critic.py brief --unit <id> --seat qa`: the return contract names no rule for a code span's edges.
2. Write a verdict whose ISSUES hold a code span starting with a space, such as `` ` full (explicit)` ``, then `critic.py record --from-verdict <file>`: refused, naming MD038.

## Proposed Fix

Add one sentence to `_RETURN_CONTRACT`: a code span in ISSUES, BLOCKING or RULINGS must not begin or end with whitespace (record refuses it, as markdownlint's MD038 would refuse the ledger); quote the value without the space and say in prose that it has one. Record's refusal is unchanged.

## Acceptance Criteria

- [ ] **AC1** Given a full-tier first-round brief from `critic.py brief`, when a reviewer reads its return contract, then the contract states that a code span must not begin or end with whitespace. Fails on: the contract says nothing about a code span's edges.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_code_span_warning.py::BriefCodeSpanWarningTests::test_the_return_contract_states_the_code_span_rule
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given a light-tier brief and a `--rejoinder` brief for the same unit, when a reviewer reads each return contract, then each states the same code-span rule. Fails on: neither says anything about it, and a fix placed in one tier's section only leaves the other silent.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_code_span_warning.py::BriefCodeSpanWarningTests::test_every_brief_kind_states_the_code_span_rule
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe; the padding alternative dropped, since `_clean` shows a padded span cannot carry the space; criteria made executable over the full, light and rejoinder briefs; Affects drops test_critic.py; Points stay 1 |
