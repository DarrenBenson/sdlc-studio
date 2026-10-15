# BG1051: The close's chain report cuts every refusal line at 160 characters, hiding which unit is blocked and why

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_close.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** close --dry-run on RUN-01M4R168, 2026-10-14: 'known-issues: 2 batch unit(s) the run cannot end over: US1004 (Draft) - ... ; BG0978 (Ope' (scratchpad log, uncut by any pipe); sprint.py:7545 `body[0][:160]`.
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T12:21:18Z

## Summary

sprint.py's chain report (sprint.py:7545-7550) slices each step's body and remedy lines to 160 characters. The close's refusals pack their substance into one line: the known-issues row lists every unit the run cannot end over, with its status and reason, separated by semicolons, so the cut lands mid-unit ('US1004 (Draft) - unfinished and not ruled in RETRO0134's carried table - findings NONE filed; BG0978 (Ope'). The dry run exists to show every refusal at once, but an operator cannot learn from it what blocks the second unit, and has to read `sprint.unanswered_units` by hand to find out.

## Steps to Reproduce

Run `sprint.py close --dry-run` on a run whose batch holds two or more units the run cannot end over: the known-issues line stops at 160 characters, inside the second unit.

## Proposed Fix

Never cut a refusal: wrap long body and remedy lines, or give each unit of a list-shaped refusal its own line, so every unit and reason is printed whole.

## Acceptance Criteria

- [ ] **AC1** Given a close whose known-issues refusal names three units with their reasons, when it runs with --dry-run, then each unit's id, status and reason is printed in full.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
