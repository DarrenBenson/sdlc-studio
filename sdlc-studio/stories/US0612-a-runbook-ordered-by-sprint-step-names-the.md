# US0612: A runbook ordered by SPRINT STEP names the one command that performs each step, its fields-file path, and the hand-rolled shape it replaces

> **Status:** Ready
> **Delivers:** CR0518
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/help/sprint.md
> **Epic:** EP0202
> **Points:** 5

## User Story

**As a** agent about to plan or run a sprint
**I want** a runbook ordered by the step I am on rather than by script name
**So that** the right command is in front of me at the moment the step arises

## Acceptance Criteria

### AC1: the runbook is ordered by sprint STEP

- **Given** the runbook as shipped
- **When** it is read
- **Then** it covers plan, groom, batch, deliver a unit, review a unit and close in that order, each naming the one command that performs it and its fields-file path where prose is involved
- **Verify:** pytest tools/tests/test_runbook.py::RunbookTests::test_every_step_names_its_command

### AC2: each step names the hand-rolled shape it replaces

- **Given** any step in the runbook
- **When** it is read
- **Then** it names what an agent would otherwise hand-roll, so the entry is findable from the wrong instinct rather than only from the right one
- **Verify:** pytest tools/tests/test_runbook.py::RunbookTests::test_each_step_names_what_it_replaces

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
