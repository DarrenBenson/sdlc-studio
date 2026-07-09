# US0105: init defaults schema_version 3 for new projects; code default stays 2 (existing projects untouched)

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0024
> **Persona:** Engineering seat
> **Affects:** scripts/init.py, scripts/lib/sdlc_md.py, scripts/tests/test_init.py, sdlc-studio/.config.yaml

## User Story

**As a** maintainer cutting v4.0
**I want** `init` to scaffold new projects at `schema_version: 3` while the code default stays 2
**So that** new projects start on the v4 schema without auto-flipping any existing (or unpinned) project

Delivers CR0198 item 1 (the default flip), scoped to be non-breaking for existing projects.

## Acceptance Criteria

### AC1: init scaffolds schema_version 3 into a new project's config

- **Given** `init` run on an empty directory
- **When** the generated `sdlc-studio/.config.yaml` is read
- **Then** it declares `schema_version: 3`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::SchemaDefaultTests

### AC2: the code default is unchanged - an unpinned project still reads as v2

- **Given** a project whose `.config.yaml` does not declare `schema_version`
- **When** `sdlc_md.schema_version` / `is_schema_v3` are evaluated
- **Then** they return 2 / False (existing and unpinned projects are never auto-flipped)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::CodeDefaultUnchangedTests

### AC3: this dogfood repo pins schema_version 2 explicitly (safety belt)

- **Given** this repository's `sdlc-studio/.config.yaml`
- **When** it is inspected
- **Then** it declares `schema_version: 2`, so no future default change silently flips it
- **Verify:** grep schema_version sdlc-studio/.config.yaml

### AC4: era-gate regression - a v2 fixture is behaviourally unchanged by the flip

- **Given** a v2 fixture project (no `schema_version` or `schema_version: 2`)
- **When** the v3-gated paths (finding vocab, triage gate) are exercised
- **Then** they stay dormant exactly as before this change
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::EraGateRegressionTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0198 item 1 (default flip, non-breaking) |
