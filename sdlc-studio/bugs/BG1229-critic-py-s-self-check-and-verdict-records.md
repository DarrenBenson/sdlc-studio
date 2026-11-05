# BG1229: critic.py's self-check and verdict records refuse shapes authors and reviewers write naturally, and record has no dry run

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_shapes.py, changelog.d/BG1229.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** run six reviews, scratchpad run6/*-verdict-r*.txt
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T15:33:48Z

## Summary

2026-11-05, run six. self-check record refuses a ruling written as 'TRUE: <evidence>' (BG1220, BG1227 builders); record has no --dry-run, so a reviewer cannot validate a verdict before handing back (US1117's untagged finding cost a reviewer resume); and the verdict ledger escapes underscores but not asterisks, so a verdict naming `test_lean_`* tripped MD037 and refused the paperwork commit.

## Steps to Reproduce

See the summary; each item was reproduced by its reviewer or builder.

## Proposed Fix

Accept a leading ruling word with the evidence kept as a field, add record --dry-run that validates without writing, and escape asterisks in the ledger as underscores are.

## Acceptance Criteria

- [ ] **AC1** A ruling 'TRUE: evidence' records as TRUE with its evidence kept; record --dry-run validates a verdict and writes nothing; a verdict naming `a_`*`_b` writes a ledger row markdownlint passes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_shapes.py

## Impact

Each costs an orchestrator hand-fix or an agent resume per unit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
