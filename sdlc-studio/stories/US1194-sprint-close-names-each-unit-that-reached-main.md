# US1194: Sprint close names each unit that reached main with no lane land record

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0326
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Sprint close names each unit that reached main with no lane land record
**So that** CR0672 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The close names a unit that reached main with no land record

- **Given** an open run whose batch holds two units, one landed by `sprint.py lane land` and one committed to the root's branch by hand with its id in the commit subject
- **When** `sprint.py close` is run
- **Then** its output carries one line naming the hand-committed unit as landed with no lane land record and the commit that carried it, and no such line for the unit `lane land` landed. Fails on: a close that says nothing of the hand commit, or names the unit `lane land` landed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseNamesUnitsWithNoLandRecordTests::test_a_hand_committed_unit_is_named_and_a_landed_one_is_not

### AC2: A unit that never reached main is not named, and the close's status is unchanged

- **Given** the same run with a third batch unit that has no commit on the root's branch since the run opened
- **When** `sprint.py close` is run with and without the hand-committed unit in the batch
- **Then** the third unit is not named as landed without a record, and the close's exit status is the same in both runs: the line is a report, not a refusal. Fails on: a carried unit reported as landed by hand, or a close refused for the missing record
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseNamesUnitsWithNoLandRecordTests::test_an_unlanded_unit_is_not_named_and_the_exit_is_unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
