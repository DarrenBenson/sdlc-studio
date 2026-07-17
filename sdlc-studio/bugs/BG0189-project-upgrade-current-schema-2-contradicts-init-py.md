# BG0189: project_upgrade.CURRENT_SCHEMA=2 contradicts init.py seeding new projects at schema_version 3

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The skill disagrees with itself about the current schema version. init.py seeds a new project from templates/config.yaml (`schema_version`: 3), so new projects ship v3. But `project_upgrade.py`:28 declares `CURRENT_SCHEMA` = 2 (commented 'templates/config-defaults.yaml `schema_version`'), and config-defaults.yaml (the merge-base fallback) plus `sdlc_md.schema_version()`'s hardcoded default are also 2. So an upgrade path that targets `CURRENT_SCHEMA` would move a project to 2, not the current 3. Surfaced while authoring reference-schema.md (EP0084): the contract had to pick a current version and the code gives two answers. The contract now correctly states 3 (D0034); this bug tracks reconciling the code so `CURRENT_SCHEMA` and the fallback-vs-current story are coherent.

## Steps to Reproduce

1. Read .claude/skills/sdlc-studio/templates/config.yaml -> `schema_version`: 3 (what init copies into new projects). 2. Read scripts/`project_upgrade.py`:28 -> `CURRENT_SCHEMA` = 2. 3. These disagree on what 'current' is; an upgrade computed against `CURRENT_SCHEMA` would not reach v3.

## Proposed Fix

Decide the single source of truth for 'current schema version' (templates/config.yaml = 3) and derive `CURRENT_SCHEMA` from it (or a shared constant), keeping config-defaults.yaml as the explicitly-named fallback. Add a test asserting init's seed == the declared current schema so the two cannot drift again.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Filed |
