# BG1079: A unit carried at the review cap gets a criterion for every ISSUES item, including info rulings and pre-existing findings already filed

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_carry.py, changelog.d/BG1079.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** sdlc-studio/bugs/BG1078-us1076-did-not-converge-in-review-round-2.md AC1 (the info item ruling round-1 findings CLOSED) and AC4 (the [pre-existing] BG1075 item), carried from US1076's round-2 REJECT, 2026-10-19; critic.py carried_criteria, `findings = [f for f in split_items(...) if f.strip(' -')]`.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T15:57:17Z

## Summary

`carried_criteria` (critic.py) turns every `;`-separated item of the capping REJECT into 'The round N REJECT finding no longer holds: <item>', whatever its origin tag. US1076's round-2 REJECT carried four items into BG1078. Two are not things a redelivery can fix: an `[new] info` item recording that every round-1 finding was CLOSED (its criterion asks that the closures 'no longer hold'), and a `[pre-existing]` item naming BG1075, already open as its own bug (a second, manual criterion for the same defect). Only the blocking item and the `low` item are the redelivery's work.

## Steps to Reproduce

Record a REJECT at the review cap whose ISSUES carries an `[new] info` item and a `[pre-existing]` item naming an open bug -> the carried bug's AC list holds a criterion for each, verified `manual`.

## Proposed Fix

Carry only the `[new]` findings that are not info; name `[pre-existing]` items (with the bug they cite) and info items in the carried bug's summary, not as criteria.

## Acceptance Criteria

- [ ] **AC1** A REJECT carried at the cap gives the carried bug a criterion for each [new] non-info finding only, and names its [pre-existing] and info items in the summary
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_carry.py -k carried_criteria_skip_info_and_pre_existing

## Impact

The carried bug cannot be closed honestly: one criterion asks for a closure to be undone, another duplicates an open bug, and the reviewer of the redelivery is briefed with both as law.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
