# US1281: Sprint plan reports a missing maintenance declaration over one third machinery and still exits 0

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0722
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0360
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Sprint plan reports a missing maintenance declaration over one third machinery and still exits 0
**So that** CR0722 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A plan over one third machinery with no declaration says so and still exits 0

- **Given** a batch whose machinery share is over one third by the path map and under it by the tags, with no maintenance declaration recorded for the run
- **When** `sprint.py plan` runs over the batch
- **Then** it prints one line naming the missing maintenance declaration, the reading that is over the cap and its figure, and exits 0 with the plan otherwise as it would be. Fails on: a plan that judges the cap on the tag reading alone and says nothing, or one that refuses the batch, which D0440 rules out
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::MaintenanceDeclarationTests::test_a_plan_over_the_cap_names_the_missing_declaration_and_exits_zero

### AC2: A recorded declaration, or a plan under the cap, prints no warning

- **Given** the same batch with a maintenance declaration naming why recorded for the run, and a second batch at or under one third machinery by both readings
- **When** `sprint.py plan` runs over each
- **Then** neither prints the missing-declaration line, and the first shows the declaration's reason beside the shares. Fails on: a warning that fires on every plan, or one that still fires after the declaration was recorded, so the line is noise the operator learns to skip
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::MaintenanceDeclarationTests::test_a_declared_or_under_cap_plan_prints_no_warning

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
