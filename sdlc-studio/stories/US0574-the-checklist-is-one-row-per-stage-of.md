# US0574: the checklist is one row per STAGE of the sprint cycle, each stating ran, not-run or waived

> **Status:** Done
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0192
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator who needs to know a full sprint cycle was followed, not just that some work shipped
**I want** the checklist to carry one row per stage of the cycle, each saying whether it ran
**So that** a stage nobody held is visible on the page rather than inferred from its absence

## Acceptance Criteria

### AC1: every stage of the cycle is a row, and each row states ran, not-run or waived

- **Given** a closed run
- **When** the sprint report is composed
- **Then** each stage of the cycle carries a row whose state is exactly one of ran, not-run or waived, and no stage is reported as an empty value - a blank reads as "nothing to say", which is the one thing a stage that never ran must not read as
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistStageTests::test_every_stage_carries_a_state_and_none_is_blank
- **Verified:** yes (2026-07-30)

### AC2: a stage that did not run is NAMED, never omitted

- **Given** a run that skipped the pre-plan goal review and produced no handoff
- **When** the report is composed
- **Then** both stages appear as not-run and are named in the rendered page, because a checklist that omits what did not happen certifies exactly the state this repo filed CR0503 about: a compulsory ceremony bypassed with nothing printed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistStageTests::test_a_stage_that_did_not_run_is_named_not_omitted
- **Verified:** yes (2026-07-30)

### AC3: the stage set cannot drift from the cycle it claims to cover

- **Given** the shipped sprint ceremony commands
- **When** the guard over the checklist runs
- **Then** every ceremony stage the cycle defines resolves to a checklist row and every row resolves to a stage, so a stage added to the cycle without a row fails rather than passing silently - a hand-maintained list is a list somebody must remember to extend, which is how the version-home list drifted through two whole files
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistStageTests::test_the_stage_set_and_the_cycle_cannot_drift_apart
- **Verified:** yes (2026-07-30)

## Summary

The compulsory set is the sprint cycle's own stages, so a stage that did not run is visible instead of inferred.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
