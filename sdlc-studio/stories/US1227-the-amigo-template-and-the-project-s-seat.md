# US1227: The amigo template and the project's seat cards carry the hand-back section, and validate seats warns if not

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0686
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/personas/amigo-template.md, sdlc-studio/personas/seats/qa.md, sdlc-studio/personas/seats/engineering.md, sdlc-studio/personas/seats/product.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0335
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The amigo template and the project's seat cards carry the hand-back section, and validate seats warns if not
**So that** CR0686 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The amigo template carries the hand-back section the shipped seats carry

- **Given** `templates/personas/amigo-template.md` and the three shipped seats under `templates/personas/amigos/`
- **When** their `## Hand-back` sections are compared
- **Then** the template has the section, and its contract lines (commands in the foreground, at most three lines naming the unit, the outcome and the hand-in path, no progress message unless blocked) are the ones the shipped seats carry; the test fails when the template or any shipped seat loses the section. Fails on: a template from which a project writes a seat card with no hand-back contract
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::AgentDefinitionTests::test_the_amigo_template_and_shipped_seats_carry_the_hand_back_section

### AC2: validate seats warns on an overriding card with no hand-back section

- **Given** a project with two seat cards under `sdlc-studio/personas/seats/` that each override a shipped seat, one with a hand-back section and one without
- **When** `validate.py seats` is run
- **Then** it prints a warning naming the card without the section, prints none for the other, and the warning alone does not change the exit code. Fails on: silence for the card that lacks it, a warning on the card that has it, or the warning raised to an error that blocks an existing project
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::SeatCheckTests::test_an_overriding_card_without_a_hand_back_section_is_warned

### AC3: This repository's seat cards carry the section

- **Given** `sdlc-studio/personas/seats/qa.md`, `engineering.md` and `product.md`
- **When** `validate.py seats` is run over this repository
- **Then** each card has the hand-back section and the run prints no hand-back warning. Fails on: a card that review briefs name still lacking the contract
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py::AgentDefinitionTests::test_this_repository_s_seat_cards_carry_the_hand_back_section

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
