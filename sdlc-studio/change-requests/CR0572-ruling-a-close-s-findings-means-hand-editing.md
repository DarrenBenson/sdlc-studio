# CR-0572: Ruling a close's findings means hand-editing one table row per finding; no bulk ruling command exists

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/help/retro.md
> **Evidence:** Stakeholder consult on CR0526's stories, RUN-01M2JA6J 2026-09-15 (sdlc-studio/reviews/consult-CR0526-stakeholders-2026-09-15.md).
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A close carrying dozens of unrepaired findings needs a Known issues carried row per finding, each written by hand. With a principal check (the ruler CR filed beside this) every close becomes that edit.

## Impact

Operators ruling a close: the cost pushes them to rubber-stamp or skip.

## Acceptance Criteria

- [ ] One command rules several findings in a named retro's carried table in one call, each row naming the ruler and date
- [ ] The command refuses a ruling word outside the carried-table vocabulary and an id no finding carries

## Recommendation

`retro.py rule --retro RETRO#### --ruling not-stop-ship --by <principal> ID...`, optionally pre-filling reviewers' proposed rulings for one-pass acceptance. Related to CR0507.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
