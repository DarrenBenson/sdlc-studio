# US0329: help/sprint.md states the single run slot and what planning a second batch against an open run does

> **Status:** Draft
> **Delivers:** CR0401
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md
> **Epic:** EP0111
> **Points:** 2

## User Story

**As an** operator reading the sprint help before planning a second batch
**I want** the help to state that there is one run slot and what planning against an
open run does
**So that** I learn the constraint from the document rather than from a fused run whose
goal verdict cannot be given honestly

## Acceptance Criteria

### AC1: the help states the slot, the refusal and the accumulating re-plan

- **Given** `.claude/skills/sdlc-studio/help/sprint.md` as shipped, read by someone who
  has never opened `run_state.py`
- **When** the reader asks what happens if a second batch is planned while a run is open
- **Then** the page answers all three parts: a project holds exactly one run at a time, a
  batch sharing no unit with the open run is refused rather than merged, and an
  overlapping re-plan accumulates into the same run
- **Verify:** manual - read help/sprint.md end to end and confirm each of the three
  statements is present and that no fourth behaviour is implied

### AC2: the help and the refusal an operator sees name the same two routes

- **Given** the refusal text delivered by US0327 beside the help page
- **When** the two are read together
- **Then** both name the same two routes, closing the open run and deliberately
  re-planning it, spelled as the same commands, so an operator following either surface
  takes the same action
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::HelpAndRefusalNameTheSameRoutesTests::test_the_refusal_and_help_sprint_name_the_same_two_routes_and_spellings

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
