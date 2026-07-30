# US0570: a unit dropped or held mid-sprint records the reason, so the report names it instead of losing it with the session

> **Status:** Draft
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0192
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator reading a sprint back a week later
**I want** a unit that was dropped or held to record why, in an artefact rather than a conversation
**So that** the reason survives the session it was decided in

## Acceptance Criteria

### AC1: a dropped unit records WHY, and the record outlives the session

- **Given** an open run holding a batch
- **When** a unit is dropped from the batch
- **Then** the drop records the reason and the report names both the unit and that reason - a drop explained in conversation is lost the moment the session ends, which is how this sprint's two held units became invisible
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchDropReasonTests::test_a_drop_records_its_reason_and_the_report_names_it

### AC2: a drop with no stated reason is REFUSED

- **Given** an open run holding a batch
- **When** a drop is attempted with no reason
- **Then** it is refused, naming the unit - an unexplained drop is indistinguishable from a unit nobody got to, and only one of those is a decision
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchDropReasonTests::test_a_drop_with_no_reason_is_refused

### AC3: HELD, DROPPED and DELIVERED are three states, not two

- **Given** a run in which one unit was delivered, one dropped, and one held pending an operator decision
- **When** the report is generated
- **Then** each is reported in its own state - a unit held on a decision is not a unit that failed and not a unit that shipped, and collapsing it into either misreports the run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchDropReasonTests::test_held_is_distinguishable_from_dropped_and_delivered

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
