# US0259: Schema version stamp as a config key plus the compatibility policy

> **Status:** Ready
> **Delivers:** RFC0047
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md
> **Epic:** EP0084
> **Points:** 3

## User Story

**As a** consumer pinning a workspace's artefact format
**I want** a machine-readable `schema_version` stamp and a stated compatibility policy
**So that** I can detect which schema a project uses and know how the format is allowed to change between versions

## Context

RFC0047 D1 resolved: the stamp is a config key - `schema_version` defaulted in `templates/config-defaults.yaml`, overridable per project like every other key, no separate marker file. The existing artefact-schema version concept (the v3 migration) supplies the current value; this story makes it declared rather than implied. The compatibility policy is the promise that makes the stamp meaningful: additive changes bump minor, renames/removals bump major and require a `migrate` path. Depends on US0258 for the `reference-schema.md` file it writes the policy section into.

## Acceptance Criteria

### AC1: config-defaults.yaml declares schema_version

- **Given** the skill's default configuration template
- **When** a project is initialised or a consumer reads its config
- **Then** a `schema_version` key exists with the current artefact-schema version as its default, with a comment stating it is the public contract stamp documented in reference-schema.md
- **Verify:** grep "schema_version" .claude/skills/sdlc-studio/templates/config-defaults.yaml

### AC2: reference-config.md documents the key

- **Given** the configuration reference
- **When** an operator looks up `schema_version`
- **Then** the key is documented: what it stamps, that consumers read it to pin a format, that `migrate` is what changes it, and that hand-editing it does not migrate anything
- **Verify:** grep "schema_version" .claude/skills/sdlc-studio/reference-config.md

### AC3: The compatibility policy is a fixed section of the contract

- **Given** `reference-schema.md` (from US0258)
- **When** a consumer reads the `Compatibility Policy` section
- **Then** it states: additive changes (new optional field, new status value, new artefact type) = minor bump; renames, removals, or semantic changes to existing surfaces = major bump with a `migrate` path shipped in the same release
- **Verify:** grep "^## Compatibility Policy" .claude/skills/sdlc-studio/reference-schema.md

### AC4: Masthead and config default agree

- **Given** the two places the current version appears (reference-schema.md masthead, config-defaults.yaml default)
- **When** either is read
- **Then** they carry the same value - single truth, no drift at ship time (US0260's guard keeps it true afterwards)
- **Verify:** shell test "$(grep -oE 'Schema version[: ]+[0-9]+' .claude/skills/sdlc-studio/reference-schema.md | grep -oE '[0-9]+$')" = "$(grep -oE 'schema_version[: ]+[0-9]+' .claude/skills/sdlc-studio/templates/config-defaults.yaml | grep -oE '[0-9]+$')"

### AC5: The change is recorded in the changelog

- **Given** the commit that ships the stamp
- **When** CHANGELOG.md is read
- **Then** the [Unreleased] section records the new `schema_version` config key and the compatibility policy
- **Verify:** grep "schema_version" CHANGELOG.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-17 | sdlc-studio | ACs groomed: 5 executable ACs incl. masthead/config agreement check; D1 resolution encoded |
