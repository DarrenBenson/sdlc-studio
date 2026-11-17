# US1308: `plan.unpinned_code` (warn by default, refuse) decides whether a batch with unpinned files is planned

> **Status:** Draft
> **Depends on:** US1307
> **Risk-class:** standard
> **Delivers:** CR0736
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_plan_unpinned_code_gate.py, changelog.d/US1308.md
> **Epic:** EP0373
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `plan.unpinned_code` (warn by default, refuse) decides whether a batch with unpinned files is planned
**So that** CR0736 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Warn is the default and plans the batch (D0517)

- **Given** no `plan.unpinned_code` key and a unit with an unpinned file
- **When** `sprint.py plan` is run
- **Then** the batch is planned and the warning is printed; the defaults file and `reference-config.md` state warn as the default. Fails on: a default of refuse, or the warning dropped
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_unpinned_code_gate.py::GateTests::test_warn_is_the_default_and_the_batch_is_planned

### AC2: Refuse stops the batch, and a pinning test clears it

- **Given** `plan.unpinned_code: refuse`
- **When** the same batch is planned, then a test importing the unpinned file is added and it is planned again
- **Then** the first plan is refused with nothing written, naming the unit, the file and the key; the second is planned. Fails on: a refusal that writes a partial plan, or one a pinning test does not clear
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_unpinned_code_gate.py::GateTests::test_refuse_stops_the_batch_and_a_pinning_test_clears_it

### AC3: An unknown value is refused by name

- **Given** `plan.unpinned_code: block`
- **When** `sprint.py plan` is run
- **Then** it is refused naming the key and its two values. Fails on: the typo read as warn
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_unpinned_code_gate.py::GateTests::test_an_unknown_value_is_refused_naming_the_two_values

## Notes

- BG0831: the key must be read by `sprint.py`, and `reference-config.md` must document only what the code honours.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
