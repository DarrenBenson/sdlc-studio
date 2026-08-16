# US0646: A shared contract reporter derives a verb's demands by executing its own guard, never by restating them

> **Status:** Ready
> **Delivers:** CR0535
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py
> **Epic:** EP0210
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A shared contract reporter derives a verb's demands by executing its own guard, never by restating them
**So that** CR0535 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: the reporter derives demands by executing the guard

- **Given** a verb whose guard refuses on a missing field
- **When** the contract reporter is asked what that verb demands
- **Then** the demand is derived by running the guard, not read from a list beside it - a restated contract drifts from the one that refuses, silently and in the direction that flatters
- **Mutant:** read the demands from a hand-maintained table - it passes today and diverges the first time a guard changes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::ContractReporterTests::test_the_demands_come_from_executing_the_guard

### AC2: a guard that changes changes the report

- **Given** the same verb after its guard gains a required field
- **When** the reporter is asked again
- **Then** the new demand appears without anyone editing a list - that is the whole difference from documentation
- **Mutant:** cache the first answer - the report is right once and wrong afterwards
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::ContractReporterTests::test_a_changed_guard_changes_the_report

### AC3: a verb with no guard says so

- **Given** a verb that refuses nothing
- **When** the reporter is asked
- **Then** it reports that the verb demands nothing, distinctly from being unable to answer - an absence and an unanswerable question are different facts
- **Mutant:** return an empty list for both - a verb the reporter cannot read looks like one with no requirements
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_contract_report.py::ContractReporterTests::test_no_guard_and_no_answer_are_different

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
