# US1186: sprint batch amend rewords a batch unit's criterion with a reason, and refuses a unit already reviewed in the run

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0656
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_amend_criterion.py
> **Epic:** EP0323
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** sprint batch amend rewords a batch unit's criterion with a reason, and refuses a unit already reviewed in the run
**So that** CR0656 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A criterion is reworded in place, with its reason on the unit and the run

- **Given** an open run whose batch holds a story with three criteria and a bug with a checkbox list
- **When** `sprint.py batch amend <id> --criterion AC2 --text <new wording> --reason <why>` runs on each
- **Then** AC2 carries the new wording, its Verify line is kept, any Verified stamp on it is removed, AC1 and AC3 are unchanged, the Revision History gains a row naming AC2 and the reason, and `batch_changes` gains an amend entry carrying the criterion and the reason. Fails on: a neighbouring criterion altered, the Verify line lost, or a reworded criterion still reading as verified
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_amend_criterion.py::BatchAmendCriterionTests::test_a_criterion_is_reworded_in_place_and_recorded

### AC2: A unit already reviewed in this run is refused

- **Given** a batch unit with a verdict recorded for it in the open run, and a second batch unit with none
- **When** `batch amend --criterion` runs on each
- **Then** the first is refused naming the recorded verdict and its file is unchanged; the second is amended. Fails on: a criterion changed beneath a verdict that judged the earlier wording
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_amend_criterion.py::BatchAmendCriterionTests::test_a_unit_already_reviewed_in_the_run_is_refused

### AC3: A criterion the unit does not carry, or an amendment missing its text or reason, is refused

- **Given** a batch unit carrying AC1 to AC3
- **When** the command names AC9, then omits `--text`, then omits `--reason`
- **Then** each exits non-zero naming the fault and neither the unit nor the run record changes. Fails on: a new criterion appended under an unknown id, or a criterion emptied
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_amend_criterion.py::BatchAmendCriterionTests::test_an_unknown_criterion_or_a_missing_text_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
