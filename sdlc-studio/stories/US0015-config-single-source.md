# US0015: Config single source

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0008, determinism-sprint)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As a** maintainer
**I want** one authoritative config source that scripts read
**So that** a default value stops living in three places (config-defaults.yaml, a
duplicate YAML fence in reference-config.md, and a prose table) and drifting (CR0008).

## Context

Implements CR0008. New `scripts/config.py` reads `templates/config-defaults.yaml`
(merged with optional project `sdlc-studio/.config.yaml`); PyYAML is a lazy soft
dependency so the stdlib core is unaffected. The 12 duplicate YAML fences in
reference-config.md are removed (defaults now live only in the YAML plus the prose
Default tables), and a drift-guard test locks those tables to the YAML.

## Acceptance Criteria

### AC1: Loader resolves defaults from the YAML, and a core script reads it

- **Given** `config-defaults.yaml` and a project `.config.yaml` that overrides one key
- **When** `get(root, "coverage.unit")` runs, and `status.py gather` runs
- **Then** the value resolves from the YAML (project overriding default), and `status` surfaces a config-derived default - a core script actually reads the single source, not a hard-coded literal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::LoadTests
- **Verified:** yes (2026-06-20)

### AC4: the loaded config is the one `status` actually reads

- **Given** a config resolved by the loader
- **When** `status` reads it end to end
- **Then** the value it uses is the value the loader resolved, which AC1's unit-level check
  cannot see - this verifier sat in AC1 unexecuted until BG0265 (see US0338 in that batch)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::IntegrationTests::test_status_reads_config
- **Verified:** yes (2026-07-22)

### AC2: No duplicate YAML fences in the reference doc

- **Given** `reference-config.md`
- **When** scanned
- **Then** it contains no ```` ```yaml ```` fences (the duplicate machine copies are gone)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::DocTests::test_no_duplicate_yaml_fences
- **Verified:** yes (2026-06-20)

### AC3: Doc Default columns guarded against drift

- **Given** the prose Default tables in `reference-config.md`
- **When** compared to `config-defaults.yaml`
- **Then** every documented numeric default equals the YAML value (drift-proof)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::DocTests::test_doc_defaults_match_yaml
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/config.py`: `load_config` / `get` (lazy PyYAML, deep-merge override) +
`show` CLI. reference-config.md: fences removed, single-source banner added.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0008) | Decomposed from CR0008 (determinism sprint) |
