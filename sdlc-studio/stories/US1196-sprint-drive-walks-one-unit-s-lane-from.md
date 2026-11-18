# US1196: Sprint drive walks one unit's lane from build to paperwork and stops with a decision record at any refusal

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive.py
> **Epic:** EP0326
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Sprint drive walks one unit's lane from build to paperwork and stops with a decision record at any refusal
**So that** CR0672 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Drive walks one unit from build to paperwork

- **Given** an open run of one Ready unit in a scratch repository, with a stub harness CLI that stages the unit's Affects and its hand-in, and a stub reviewer that returns an APPROVE
- **When** `sprint.py drive` is run
- **Then** it runs the headless build, `lane land`, the QA brief, the review, `lane accept`, the priced return and the paperwork commit in that order, printing one line per step; the unit ends Done, the paperwork is committed and the exit is 0. Fails on: a walk that skips or reorders a step, or leaves the unit's paperwork uncommitted at exit 0
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive.py::SprintDriveTests::test_a_clean_unit_is_driven_from_build_to_paperwork

### AC2: A step that exits non-zero stops the walk with a one-screen decision record

- **Given** the same run with a commit hook that refuses the landing
- **When** `sprint.py drive` is run
- **Then** no step after the landing runs, the exit is non-zero, and the decision record is at most 30 lines naming the unit, the step that stopped, its exit status, the last lines of its output, where the whole output is kept and the command that resumes; the unit is not Done. Fails on: a walk that briefs or accepts after a refused landing, or a record that prints the whole hook log
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive.py::SprintDriveTests::test_a_refused_step_stops_the_walk_with_a_decision_record

### AC3: A REJECT stops the walk and names the repair

- **Given** the same run with a stub reviewer that returns a REJECT with one BLOCKING finding
- **When** `sprint.py drive` is run
- **Then** the verdict is recorded, the unit is not moved, no priced return or paperwork commit runs, and the decision record quotes the blocking finding and names the repair-scope brief command. Fails on: a REJECT followed by the unit moving to Done, or by drive spawning a repair itself
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive.py::SprintDriveTests::test_a_reject_stops_the_walk_and_names_the_repair_brief

### AC4: The help and the reference name drive and each of its stops

- **Given** `help/sprint.md`, `reference-sprint.md` and `sprint.py drive --help`
- **When** each is read
- **Then** all three name the steps drive walks and the stops it makes (a non-zero exit, a warning, a REJECT, a rebase conflict, a wave end), and every flag the pages name is one the parser accepts. Fails on: a page naming a stop the code does not make or a flag the parser refuses, or `drive` absent from the help
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive.py::SprintDriveTests::test_the_help_and_reference_name_each_stop

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
