# US1223: Critic record takes a defect class on each blocking finding and the sprint report counts blockers by class

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0682
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0333
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Critic record takes a defect class on each blocking finding and the sprint report counts blockers by class
**So that** CR0682 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A blocking finding keeps the defect class recorded after its origin tag

- **Given** a unit with an issued brief and a REJECT whose blocking finding names one of the seven defect classes (sweep-red, vacuous-pin, proxy-observable, unstated-invariant, external-format, doc-drift, other) after its origin tag
- **When** the verdict is recorded with `critic.py record`
- **Then** the ledger row keeps the class with that finding, and critic's reader of the row returns the finding's origin, its class and its text as three separate values. Fails on: a class dropped from the row, or read back as part of the finding's text
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::DefectClassTests::test_a_blocking_finding_keeps_the_class_recorded_after_its_origin_tag

### AC2: A class outside the list is refused and an untagged finding still records

- **Given** one REJECT whose finding carries a class outside the seven, and a second whose finding carries an origin tag and no class
- **When** each is recorded with `critic.py record`
- **Then** the first is refused with a message that lists the seven classes and writes no row, and the second is recorded as before and read back as unclassified. Fails on: a misspelt class recorded as given, or a finding refused only because it names no class
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::DefectClassTests::test_an_unknown_class_is_refused_and_an_untagged_finding_still_records

### AC3: The sprint report's unit table counts round-1 blockers by class

- **Given** a run whose ledger holds round-1 REJECTs with classed blocking findings on two units, an unclassed blocking finding on one of them, and a round-2 REJECT with a further classed finding
- **When** the sprint report is rendered through `sprint_report.py`
- **Then** each unit's row in the unit table states its round-1 blockers by class, the unclassed finding is counted as unclassified, and the round-2 finding and any pre-existing finding are counted in no class. Fails on: a round-2 or pre-existing finding added to the count, or an unclassed blocker shown as none
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::BlockersByClassTests::test_the_unit_table_counts_round_one_blockers_by_class

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
