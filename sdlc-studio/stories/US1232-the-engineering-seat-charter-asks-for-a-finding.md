# US1232: The engineering seat charter asks for a finding on an undeclared failure path and a note on a missing section

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0691
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/personas/amigos/engineering.md, sdlc-studio/personas/seats/engineering.md, .claude/skills/sdlc-studio/scripts/tests/test_engineering_seat_reliability.py
> **Epic:** EP0338
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The engineering seat charter asks for a finding on an undeclared failure path and a note on a missing section
**So that** CR0691 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Both engineering cards ask for a finding on a failure path that departs from the declaration

- **Given** the shipped engineering amigo card and this repository's engineering seat card
- **When** each card's review lens is read
- **Then** each asks the reviewer for a finding when a change's failure path differs from the behaviour the TRD declares for the component, or emits none of the required signals. Fails on: the rule on the shipped card only, so this repository's override card reviews without it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engineering_seat_reliability.py::EngineeringSeatReliabilityTests::test_both_cards_ask_for_a_finding_on_a_departing_failure_path

### AC2: Both cards treat a missing declaration as a note

- **Given** the same two cards
- **When** each card's rule for a component the TRD does not declare, or a TRD with no such section, is read
- **Then** each says a missing declaration is reported as a note and is not grounds for a REJECT. Fails on: a card that leaves the verdict open, so a project that has not yet written the section has every unit rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engineering_seat_reliability.py::EngineeringSeatReliabilityTests::test_both_cards_treat_a_missing_declaration_as_a_note

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
