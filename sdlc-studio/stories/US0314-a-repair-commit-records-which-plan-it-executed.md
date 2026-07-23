# US0314: A repair commit records which plan it executed, so a planned repair is distinguishable from an unplanned one

> **Status:** Draft
> **Verification depth:** functional - node-addressed tests in test_repair_plan.py / test_critic.py, all green; EP0106 mutation-proven (11 mutants across record_repair_plan, review, gate, pin, provenance, all killed)
> **Delivers:** RFC0053
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/reference-review.md
> **Epic:** EP0106
> **Points:** 2

## User Story

**As a** later reader of the history
**I want** a repair commit to name the plan it executed
**So that** a planned repair is distinguishable from an unplanned one without reconstructing
the sprint from its artefacts

## Acceptance Criteria

### AC1: a repair recorded against a sprint names its plan

- **Given** a repair recorded after a REJECT
- **When** the sprint's review round is written to the run state
- **Then** the round carries the plan id the repair executed, and the close can report which
  rounds were planned and which were not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairProvenanceTests::test_a_recorded_repair_carries_the_plan_it_executed

### AC2: an unplanned repair is recorded as unplanned, never as absent

- **Given** a repair recorded while the gate is off, so no plan exists
- **When** the round is written
- **Then** it records that no plan was executed, explicitly, rather than leaving the field
  empty - an absent field reads as missing data, and a reader cannot tell it apart from a
  planned repair whose id was dropped
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairProvenanceTests::test_an_unplanned_repair_is_recorded_as_unplanned_not_blank

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
