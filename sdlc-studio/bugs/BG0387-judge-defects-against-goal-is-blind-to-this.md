# BG0387: judge_defects_against_goal is blind to this repo's priority vocabulary, so every High is ruled leavable

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
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

### AC1: a High-severity defect blocks, against this repo's own vocabulary

- **Given** a defect filed `Severity: High`, the word this corpus uses 104 times
- **When** it is judged against the goal
- **Then** it is BLOCKING, not leavable
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BlockingPriorityFloorTests::test_a_high_severity_defect_blocks_against_this_repos_own_vocabulary
- **Verified:** yes (2026-07-29)

### AC2: the reviewer's word and the filer's word are one tier

- **Given** a defect at `Major`, the word an adversarial reviewer writes
- **When** it is judged
- **Then** it blocks exactly as `High` does, so the cut does not depend on which word was typed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BlockingPriorityFloorTests::test_major_is_the_same_tier_as_high
- **Verified:** yes (2026-07-29)

### AC3: a decorated value is normalised before comparing

- **Given** `**High**`, `High (severity)`, `P1` or `Sev-1`
- **When** each is judged
- **Then** all block, because a decorated value compared raw is a value that never matches
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BlockingPriorityFloorTests::test_a_decorated_value_is_normalised_before_comparing
- **Verified:** yes (2026-07-29)

### AC4: the floor is derived from one cut, not an enumerated list

- **Given** a project that moves `review.blocking_priority`
- **When** the floor is read
- **Then** it is the tiers at or above that cut, so a project changes ONE value rather than keeping a list of synonyms in step with its own vocabulary
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BlockingPriorityFloorTests::test_the_floor_is_derived_from_one_cut_not_an_enumerated_list
- **Verified:** yes (2026-07-29)

### AC5: an unconfigurable floor never becomes an absent one

- **Given** a cut the ordering does not recognise
- **When** the floor is read
- **Then** it falls back to the shipped default, because a floor nobody configured must not silently become no floor at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BlockingPriorityFloorTests::test_an_unrecognised_cut_falls_back_rather_than_emptying_the_floor
- **Verified:** yes (2026-07-29)

### AC6: a defect below the cut is still recorded, never dropped

- **Given** defects at Low and Medium
- **When** they are judged
- **Then** neither blocks and both are recorded as leavable with their reasoning, because shipping with a known defect is a decision and one nobody wrote down is indistinguishable from not having noticed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BlockingPriorityFloorTests::test_below_the_cut_is_still_leavable_and_recorded
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
