# US1287: The three unreferenced persona prompt templates are retired or rewired, and a test fails on an unnamed persona template

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0726
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/personas/prompts/code-analysis-prompt.md, .claude/skills/sdlc-studio/templates/personas/prompts/discovery-presentation.md, .claude/skills/sdlc-studio/templates/personas/prompts/enrichment-questions.md, .claude/skills/sdlc-studio/reference-persona-generate.md, tools/tests/test_persona_templates_referenced.py
> **Epic:** EP0364
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The three unreferenced persona prompt templates are retired or rewired, and a test fails on an unnamed persona template
**So that** CR0726 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each of the three prompts is removed or named for a step

- **Given** `code-analysis-prompt.md`, `discovery-presentation.md` and `enrichment-questions.md` under `templates/personas/prompts/`, and `reference-persona-generate.md`
- **When** the directory and the reference page are read
- **Then** each file is either absent from the shipped skill, or named by its path in `reference-persona-generate.md` as the prompt loaded for a stated step of persona generation; a section that merely shares a file's name does not count. Fails on: a prompt that still ships and that no step loads
- **Verify:** pytest tools/tests/test_persona_templates_referenced.py::PersonaPromptTests::test_each_persona_prompt_is_removed_or_named_for_a_step

### AC2: A prompt that is kept follows the current persona model

- **Given** every file still under `templates/personas/prompts/`, and `persona-template.md`
- **When** each kept file is read, and the same check is run on a fixture prompt that classifies a persona as Team
- **Then** each kept file asks for the Cast role and the End Goals `persona-template.md` requires and does not classify a persona as Team to be assigned to an amigo, and the fixture fails the check. Fails on: a kept prompt that still produces a card the persona template would reject
- **Verify:** pytest tools/tests/test_persona_templates_referenced.py::PersonaPromptTests::test_a_kept_prompt_asks_for_cast_role_and_end_goals

### AC3: A persona template nothing names fails the reference test

- **Given** a throwaway copy of the skill with one extra file added under `templates/personas/prompts/` that no reference page, help page or script names, and the live skill tree
- **When** the reference check is run over each
- **Then** it names the extra file in the copy and passes on the live tree with no exemption for a file under `templates/personas/prompts/`; the only exemption allowed is one naming `review-seat-charter.md` while US1174 is not yet Done. Fails on: a check that skips the prompts directory, or one that passes a file nothing loads
- **Verify:** pytest tools/tests/test_persona_templates_referenced.py::PersonaPromptTests::test_an_unnamed_file_under_prompts_is_caught

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
