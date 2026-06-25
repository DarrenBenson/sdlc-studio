# CR-0119: project upgrade installs the v3.1 amigo defaults into consuming projects

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

project_upgrade.py migrates a consuming project to the current skill conventions. v3.1 ships the enriched amigo defaults (templates/personas/amigos/ - Engineering/QA/Product, editable per project, RFC0020). An upgrading project should be offered/installed those amigo cards so it gets the personal engineering team it can edit, and the upgrade should note the v3.1 persona enrichment. Must be idempotent and never clobber a project's already-customised amigos.

## Acceptance Criteria

- [x] project upgrade installs the three default amigo cards into the project's persona directory when absent (part of the safe set or offered), so the project has an editable engineering team
- [x] idempotent - a project that already has amigos (customised) is not overwritten; the upgrade reports what it added
- [x] the v3.1 persona enrichment is noted in the upgrade output + reference-upgrade.md; unit test covers install-when-absent and skip-when-present; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Raised |
