# US0447: A shared reader parses the design-persona registry into Primary, Secondary and Negative with their card paths

> **Status:** Ready
> **Delivers:** CR0425
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Epic:** EP0166
> **Points:** 3

## User Story

**As a** skill maintainer wiring the persona layer into the pipeline
**I want** one shared reader that parses the design-persona registry into its Primary, Secondary and Negative entries with their card paths
**So that** every command needing to know who the product is for derives it from the registry, rather than restating a list that drifts

## Acceptance Criteria

### AC1: the reader returns each declared role with its name and card path

- **Given** a `personas/index.md` declaring a Primary, a Secondary and a Negative persona
- **When** the shared reader parses it
- **Then** it returns each persona's name, its declared role, and its card path resolved against the workspace
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::PersonaRegistryTests::test_registry_parses_each_declared_role

### AC2: an absent or unparseable registry is distinguishable from one declaring nobody

- **Given** a workspace with no `personas/index.md`, or one whose role headings cannot be parsed
- **When** the reader runs
- **Then** it reports that absence explicitly for the caller to handle, never an empty result indistinguishable from a registry that genuinely declares no personas
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::PersonaRegistryTests::test_absent_registry_is_distinguishable_from_empty

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: user story and acceptance criteria authored against the slice |
