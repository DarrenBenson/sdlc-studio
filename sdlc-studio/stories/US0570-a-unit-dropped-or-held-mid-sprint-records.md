# US0570: a unit dropped or held mid-sprint records the reason, so the report names it instead of losing it with the session

> **Status:** Done
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0192
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator reading a sprint back a week later
**I want** a unit that was dropped or held to record why, in an artefact rather than a conversation
**So that** the reason survives the session it was decided in

## Acceptance Criteria

### AC1: the report NAMES each dropped unit with the reason recorded against it

- **Given** a closed run whose batch-change ledger holds drops with their reasons
- **When** the report is composed
- **Then** it names each dropped unit beside its recorded reason, rather than reporting a smaller batch and leaving the difference to be noticed - the recording half already refuses a reasonless drop, and a reason nothing reads is a reason nobody sees
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistNotDeliveredTests::test_the_report_names_each_dropped_unit_with_its_reason
- **Verified:** yes (2026-07-30)

### AC2: HELD, DROPPED and DELIVERED are three states, not two

- **Given** a run in which one unit was delivered, one dropped, and one held pending an operator decision
- **When** the report is composed
- **Then** each is reported in its own state - a unit held on a decision is not a unit that failed and not a unit that shipped, and collapsing it into either misreports the run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistNotDeliveredTests::test_held_is_distinguishable_from_dropped_and_delivered
- **Verified:** yes (2026-07-30)

### AC3: a unit that was neither delivered nor dropped is reported as CARRY-OVER

- **Given** a run whose approved batch still holds a unit at a non-terminal status at the close
- **When** the report is composed
- **Then** it is reported as carry-over rather than silently absent from both the delivered and the dropped lists, so the planned set always reconciles - delivered plus dropped plus held plus carry-over, with no unit unaccounted for
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistNotDeliveredTests::test_the_planned_set_reconciles_with_no_unit_unaccounted_for
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-30 | sdlc-studio | Retargeted at planning: the recording half already ships (`run_state.drop_from_batch` raises on a blank reason, `sprint batch drop` exits 2 without one, both tested), so the ACs now cover the unshipped half - the report naming the drop, the held state, and carry-over. |
