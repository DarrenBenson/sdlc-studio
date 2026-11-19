# US1185: sprint batch amend widens a batch unit's Affects with a reason, writes its revision row and records it on the run

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0656
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_batch_amend_affects.py
> **Epic:** EP0323
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** sprint batch amend widens a batch unit's Affects with a reason, writes its revision row and records it on the run
**So that** CR0656 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: An amendment widens the Affects, writes the revision row and lands on the run

- **Given** an open run with a story in its batch
- **When** `sprint.py batch amend <id> --affects-add <path> <path> --reason <why>` runs, one of the paths being already declared
- **Then** the unit's Affects line lists its former paths followed by the new one once, its Revision History gains a row naming the reason, and the run record's `batch_changes` gains an amend entry carrying the unit, the paths added, the reason and a timestamp. Fails on: an Affects line edited with no revision row or no run record, which is the hand edit CR0656 describes, or a path listed twice
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_amend_affects.py::BatchAmendAffectsTests::test_an_amendment_widens_the_affects_and_is_recorded

### AC2: An amendment without a reason, a batch unit or an open run is refused and changes nothing

- **Given** a unit in the batch, a unit outside it, and a tree with no run open
- **When** `batch amend --affects-add` runs with a blank `--reason`, then against the unit outside the batch, then with no run open
- **Then** each exits non-zero naming what is missing, and the unit file and the run record are byte-identical afterwards; the same command with a reason against the batch unit succeeds. Fails on: an unrecorded amendment, or the scope of a unit outside the plan widened
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_amend_affects.py::BatchAmendAffectsTests::test_an_amendment_without_a_reason_or_a_batch_unit_is_refused

### AC3: The runbook and the sprint help name the command the parser accepts

- **Given** the in-flight table of `reference-sprint-toolchain.md` and `help/sprint.md`
- **When** an orchestrator looks up how to widen a planned unit's scope
- **Then** each names `sprint.py batch amend` with `--affects-add` and `--reason`, and the command as written there parses. Fails on: a runbook row for a command the parser refuses, or the step still having no command
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_amend_affects.py::BatchAmendAffectsTests::test_the_runbook_and_help_name_the_amend_command

## Further evidence

- 2026-11-18, the website's RUN-01M7R7KN: a lane found tests/data.test.ts pinning the agents list
  its unit's criterion changes, outside both its units' Affects. The orchestrator hand-edited the
  story's Affects on main and recorded the website's D0023; CR0744 was filed for the same command
  and rejected as a duplicate of CR0656.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
