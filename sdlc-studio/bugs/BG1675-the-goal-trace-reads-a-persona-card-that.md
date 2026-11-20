# BG1675: The goal trace reads a persona card that is not UTF-8 as empty, so a goal naming that persona is briefed as naming nobody and its card-not-utf8 hold never refuses the goal review

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_persona_block.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T16:56:08Z

## Summary

US1056's round-three engineering review (RUN-01M7VNR0) found that `_persona_card_entries` reads each card through `sdlc_md.read_text_safe` (sprint.py around 11788), which returns an empty text for a card that is not valid UTF-8, so the card names nobody: a goal naming that persona is briefed as naming no persona, and the card-not-utf8 hold that the docs say always blocks never refuses the goal review. Pre-existing (the same read at 958701b5).

## Steps to Reproduce

Put a 0xe9 byte in a traced persona card (Jonah Reyes) and run sprint.py goal-review brief --goal 'Jonah Reyes upgrades without a surprise': the brief names no persona and is not refused.

## Proposed Fix

Read cards in the goal trace with replacement (`validate.read_card)`, so the card still names its persona and the card-not-utf8 hold refuses the brief; pin it in `test_goal_review_persona_block.py.`

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1056's round-three engineering review (RUN-01M7VNR0) found that `_persona_card_entries` reads each card through `sdlc_md.read_text_safe` (sprint.py around...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Put a 0xe9 byte in a traced persona card (Jonah Reyes) and run sprint.py goal-review brief --goal 'Jonah Reyes upgrades without a surprise': the brief names no...
- [ ] **AC3** The proposed fix lands, pinned by a test: Read cards in the goal trace with replacement (`validate.read_card)`, so the card still names its persona and the card-not-utf8 hold refuses the brief; pin it...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
