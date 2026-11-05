# BG1232: The lane brief's budget and hand-in: no-Points untested, one shared hand-in for a multi-unit lane, and US1093's stale story text

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_followups.py, changelog.d/BG1232.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run six reviews, scratchpad run6/*-verdict-r*.txt
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T15:34:35Z

## Summary

2026-11-05, US1120's build and review. A unit with no Points is untested (removing the None check crashes lane brief; None as 0 prints 25); in a multi-unit lane every unit points at one shared commit-msg.txt and HANDOFF.md, each with its own budget and no lane total; US1093's story text still says the brief carries the self-check record command; `LANE_HAND_IN` may duplicate a path constant in lib/lanes.py.

## Steps to Reproduce

See the summary; each item was reproduced by its reviewer or builder.

## Proposed Fix

Pin the no-Points branch, give a multi-unit lane one budget and per-unit hand-in names, share one hand-in constant, and correct US1093's text.

## Acceptance Criteria

- [ ] **AC1** A no-Points unit's brief says NONE DERIVED and a test fails if the check is removed; a two-unit lane's brief names per-unit hand-in files and one lane budget; one constant names the hand-in path.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_followups.py

## Impact

A multi-unit lane following the brief literally lands every unit under one subject.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
