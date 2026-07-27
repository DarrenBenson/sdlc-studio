# US0448: artifact.py resolves --persona through the registry: the declared Primary by default, a warning on an unregistered name, a refusal under strict

> **Status:** Review
> **Delivers:** CR0425
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0166
> **Points:** 3

## User Story

**As an** agent minting a story through the mandated deterministic path
**I want** `--persona` resolved against the registry, defaulting to the declared Primary
**So that** the persona a story serves is a real design target rather than free text nothing downstream consumes

## Acceptance Criteria

### AC1: an omitted persona defaults to the declared Primary

- **Given** a workspace whose registry declares a Primary
- **When** a story is minted with no `--persona`
- **Then** the story's Persona line names that Primary, resolved from the registry
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::PersonaResolutionTests::test_omitted_persona_defaults_to_the_declared_primary
- **Verified:** yes (2026-07-27)

### AC2: an unregistered name warns, and refuses under strict

- **Given** `--persona` naming someone the registry does not declare
- **When** the story is minted, and again under `--strict`
- **Then** the default path mints it with a warning naming the registered personas, and the strict path refuses and mints nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::PersonaResolutionTests::test_unregistered_persona_warns_and_strict_refuses
- **Verified:** yes (2026-07-27)

### AC3: naming the Negative persona warns but is never refused

- **Given** `--persona` naming the registry's Negative persona
- **When** the story is minted, with or without `--strict`
- **Then** it is minted carrying a warning that it serves the negative design target, and is refused on neither path - the ruling recorded as D0066
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::PersonaResolutionTests::test_negative_persona_warns_but_is_never_refused
- **Verified:** yes (2026-07-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: user story and acceptance criteria authored against the slice |
