# US1174: The review seat charter pointer template is removed and the persona template reference test covers pointer files

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0727
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/personas/review-seat-charter.md, tools/tests/test_persona_templates_referenced.py
> **Epic:** EP0315
> **Points:** 1
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The review seat charter pointer template is removed and the persona template reference test covers pointer files
**So that** CR0727 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The pointer template is gone and nothing expects it

- **Given** the shipped skill, `install.sh`, `install.ps1` and `tools/`
- **When** the tree is searched for `review-seat-charter.md`
- **Then** `templates/personas/review-seat-charter.md` does not exist, and no file names its path as one to read, copy or link (the fixture string in `tools/tests/test_check_neutrality.py`, which does not need the file, is the one mention left). Fails on: the pointer still shipped, or an installer or reference line that would break on its absence
- **Verify:** pytest tools/tests/test_persona_templates_referenced.py::PersonaTemplatesReferencedTests::test_the_review_seat_charter_pointer_is_gone_and_nothing_expects_it

### AC2: A persona template nothing names fails the reference test

- **Given** a throwaway copy of the skill with one extra file added under `templates/personas/` that no reference page, help page or script names, and the live skill tree
- **When** the reference check is run over each
- **Then** it names the extra file in the copy and passes on the live tree, with no exemption for `review-seat-charter.md`; the only exemption allowed is one naming the three files under `templates/personas/prompts/` while US1287 is not yet Done. Fails on: a check that passes a pointer kept for references that no longer exist, or one that matches a bare file name inside the file itself
- **Verify:** pytest tools/tests/test_persona_templates_referenced.py::PersonaTemplatesReferencedTests::test_a_persona_template_nothing_names_is_caught

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
