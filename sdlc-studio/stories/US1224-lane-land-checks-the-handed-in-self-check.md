# US1224: Lane land checks the handed-in self-check claims before it commits, and the brief names one fragment label

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0683
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py
> **Epic:** EP0334
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Lane land checks the handed-in self-check claims before it commits, and the brief names one fragment label
**So that** CR0683 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A hand-in the self-check refuses is refused before any commit

- **Given** a lane worktree with a staged change, a commit message and a hand-in whose self-check claims `critic.py self-check record` refuses (the shape of US1122: fragment claims labelled CHANGELOG)
- **When** `sprint.py lane land --worktree <path> --units <id>` is run
- **Then** it exits non-zero naming the unit and the offending label, the lane branch and main each hold no new commit, and the staged change is still staged in the worktree. Fails on: the refusal printed after the commit has landed, as lane land does today
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_hand_in_the_self_check_refuses_is_refused_before_any_commit

### AC2: A valid hand-in still lands with its self-check recorded once

- **Given** the same lane with a hand-in whose claims the self-check accepts
- **When** `sprint.py lane land` is run
- **Then** the change is committed and fast-forwarded onto main, the unit's self-check is recorded exactly once and its QA brief is written. Fails on: an early check that refuses a valid hand-in, or one that records the self-check twice
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_valid_hand_in_lands_with_its_self_check_recorded_once

### AC3: The lane brief names one label for a fragment claim

- **Given** a planned unit whose Affects names its `changelog.d` fragment
- **When** its lane brief is printed with `sprint.py lane brief`
- **Then** the claim inventory names a fragment claim by one label only, and a hand-in that uses that label is accepted by lane land. Fails on: a brief that offers both CHANGELOG and the fragment path as labels, or one whose single label the self-check then refuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_the_lane_brief_names_one_label_for_a_fragment_claim

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
