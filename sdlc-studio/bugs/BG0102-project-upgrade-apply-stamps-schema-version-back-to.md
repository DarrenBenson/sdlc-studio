# BG0102: project upgrade --apply stamps schema_version back to 2 on a schema-3 project

> **Status:** In Progress
> **Verification depth:** functional (red-then-green: project upgrade --apply on a schema-3 project with an older skill stamp now preserves schema_version: 3 in .version - max(effective, CURRENT_SCHEMA), an upgrade can only raise the stamp; suite 1571)
> **Severity:** Medium
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

`project_upgrade._bump_version_text` writes `schema_version`: `CURRENT_SCHEMA` (a constant 2) unconditionally into .version. Run 'project upgrade --apply' on a project that has completed the v2->v3 migration (`schema_version`: 3 in .config.yaml and .version) and its .version stamp is silently rewritten to `schema_version`: 2 - the version marker now contradicts the workspace's actual era. Found while implementing CR0216 (the numbering-switch consent work touches the same flow).

## Steps to Reproduce

1. Project at schema 3 (.config.yaml and .version both say 3). 2. Run `project_upgrade` --apply (e.g. after a skill version bump). 3. .version now reads `schema_version`: 2 while the workspace mints ULIDs.

## Proposed Fix

Stamp max(project effective schema, `CURRENT_SCHEMA)`, never a blind constant: pass the resolved schema into `_bump_version_text` so an upgrade can only ever raise the stamp.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
