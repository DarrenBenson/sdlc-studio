# BG0070: migrate_v3 build_id_map runs a git log --follow per artefact, so it does not scale to a large project

> **Status:** Fixed
> **Severity:** High
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (unit regression test asserts <=1 git call, plus re-rehearsed dry-run on two real ~1,500-artefact projects: >150s -> 0.2-0.3s)

## Summary

v4 migration rehearsal (US0106) on two real consuming projects surfaced a scale defect. build_id_map calls _file_epoch_ms per artefact, which spawns 'git log --diff-filter=A --follow -1' for each file. On a ~1700-file project migrate_v3 plan is very slow; on a ~1945-file project build_id_map + migrate(dry_run) did not complete within 150s. --follow is especially slow, and one subprocess per file gives thousands of git invocations. The v4 upgrade path is impractical on a real large project.

## Steps to Reproduce

Run migrate_v3.py plan --root <project with ~2000 artefacts> (e.g. a mature consuming repo); observe it not completing within a couple of minutes; time build_id_map and see the cost is per-file git log --follow subprocesses.

## Proposed Fix

Batch the creation-date lookup into a single git pass (e.g. one 'git log --diff-filter=A --name-only --format' walk building a path->first-commit-epoch map), or drop --follow, or cache; fall back to mtime once. Target: build_id_map on 2000 artefacts in a few seconds, not minutes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
