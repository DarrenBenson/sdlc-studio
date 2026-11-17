# US1309: The brownfield runbook has a pin-behaviour stage before the first code change, with its done test

> **Status:** Draft
> **Depends on:** US1308
> **Risk-class:** standard
> **Delivers:** CR0736
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/brownfield-runbook.md, tools/tests/test_brownfield_runbook_pin_stage.py, changelog.d/US1309.md
> **Epic:** EP0373
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The brownfield runbook has a pin-behaviour stage before the first code change, with its done test
**So that** CR0736 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The runbook pins behaviour before the first change

- **Given** `help/brownfield-runbook.md`
- **When** it is read
- **Then** a numbered stage between extraction and change tells the reader to write characterisation tests that assert what the code does now, including results that look wrong, says it is done when `sprint plan` names no unpinned file for the batch, and links `plan.unpinned_code` in `reference-config.md`. Fails on: the stage placed after the first change, or a done test that cannot be run
- **Verify:** pytest tools/tests/test_brownfield_runbook_pin_stage.py::PinStageTests::test_the_runbook_has_a_pin_stage_before_the_first_change

### AC2: The page passes the repository's page checks

- **Given** the changed page
- **When** `tools/check_links.py` and `tools/lint-style.sh` are run
- **Then** both pass. Fails on: a broken anchor to the config key, or an em dash
- **Verify:** pytest tools/tests/test_brownfield_runbook_pin_stage.py::PinStageTests::test_the_page_passes_the_link_and_style_checks

## Notes

- The stage's wording uses the term characterisation test, which appears nowhere in the skill today; define it in one sentence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
