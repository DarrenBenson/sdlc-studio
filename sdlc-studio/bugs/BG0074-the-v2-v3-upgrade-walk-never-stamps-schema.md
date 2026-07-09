# BG0074: the v2->v3 upgrade walk never stamps schema_version: 3, so the next filing mints ids that collide with live aliases

> **Status:** Open
> **Severity:** High
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: BLOCKS v4.0 tag. migrate_v3's docstring says schema_version 'should be set' manually (migrate_v3.py:17-18); project_upgrade's migration_walk has no schema-flip step (project_upgrade.py:162-179) and its _CONFIG scaffold pins CURRENT_SCHEMA = 2 (:28,:47). After a clean migrate all numeric ids vanish from files and index rows, so allocate_number restarts at 1. Reproduced (RV0007): migrate_v3 apply, then artifact.py new --type bug -> 'created BG0001' while the migrated BG-01KX4E00 still carries '> **Aliases:** BG0001' - external references, GitHub aliases and commit messages using BG0001 now resolve ambiguously. The documented walk, followed verbatim, leaves a consuming project one 'artifact new' away from identity collision.

## Steps to Reproduce

v2 fixture; migrate_v3.py apply; artifact.py new --type bug --title x -> BG0001 minted; grep 'Aliases: BG0001' -> live alias on a different artefact.

## Proposed Fix

migrate_v3 apply writes schema_version: 3 into .config.yaml itself; belt-and-braces, allocate_number treats alias ids as taken.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
