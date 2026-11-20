# BG1664: persona_cards still builds the number-keyed goal_verify and goal_applies_to maps that nothing reads after BG1660

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T11:35:44Z

## Summary

BG1660's engineering review (RUN-01M7VNR0) found that after b730b6c7 nothing in the shipped scripts reads `goal_verify` (sprint.py around 11785) or `goal_applies_to`: `goal_trace` now reads the goals list. `persona_cards` still builds both number-keyed maps beside the correct list, which is the shape that let two goals numbered alike share one Verify (BG1660), with only a docstring sentence warning a future caller off them. Dead state that invites the old bug back.

## Steps to Reproduce

grep -n `goal_verify` and `goal_applies_to` across .claude/skills/sdlc-studio/scripts: the only writes are in `persona_cards` and no caller reads either key.

## Proposed Fix

Drop both keys from `persona_cards`' return value, or derive them from goals where a caller needs them, with a test that a card numbered 1. 1. keeps both goals.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1660's engineering review (RUN-01M7VNR0) found that after b730b6c7 nothing in the shipped scripts reads `goal_verify` (sprint.py around 11785) or...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: grep -n `goal_verify` and `goal_applies_to` across .claude/skills/sdlc-studio/scripts: the only writes are in `persona_cards` and no caller reads either key.
- [ ] **AC3** The proposed fix lands, pinned by a test: Drop both keys from `persona_cards`' return value, or derive them from goals where a caller needs them, with a test that a card numbered 1.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
