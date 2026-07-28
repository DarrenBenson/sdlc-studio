# BG0387: judge_defects_against_goal is blind to this repo's priority vocabulary, so every High is ruled leavable

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`BLOCKING_PRIORITIES` is `p0/p1/critical/blocker`. This corpus uses High/Medium/Low: 104 `Severity: High` bugs and 168 `Priority: High` CRs against 2 Critical and 13 P1. So the severity floor never fires on the words this project actually files under, and `major` - the word an adversarial reviewer uses - is leavable too.

## Steps to Reproduce

`judge_defects_against_goal([`{'id':'BG0370','severity':'High'}], ['every seam has an owner']) -> LEAVABLE

## Proposed Fix

Include `high` and `major`, and normalise a decorated field value before comparing.

## Acceptance Criteria

- [ ] A High-severity defect blocks the close, pinned against this repo's own vocabulary.
- [ ] The floor is derived from the project's declared priority values rather than a list this file keeps.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
