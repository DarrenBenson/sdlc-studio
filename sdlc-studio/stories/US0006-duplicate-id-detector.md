# US0006: Deterministic duplicate-ID detector

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint loop
> **Reviewer:** Independent critic (APPROVE)
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As a** skill maintainer
**I want** a deterministic check that flags two or more artifact files sharing one ID
**So that** ID collisions (the failure mode the doctrine warns about, and that hit eight times historically) are caught automatically instead of by eye.

## Context

Implements CR0002. `next_id.py` allocated the next free ID but never audited for existing collisions, and reconcile/status key on the normalised ID so a duplicate is silently collapsed. This adds a read-only detector.

## Acceptance Criteria

### AC1: Group artifact files by normalised ID

- **Given** a workspace containing `CR0007.md` and `CR-0007.md`
- **When** the detector runs
- **Then** both collapse to one normalised key `CR0007` (dash-insensitive)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_duplicate_id.py::GroupingTests::test_dash_insensitive_normalisation

### AC2: Flag any ID owned by more than one distinct file

- **Given** two distinct files `BG0001-a.md` and `BG0001-b.md`
- **When** the detector runs
- **Then** it reports `BG0001` as a duplicate and lists both paths
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_duplicate_id.py::DetectTests::test_two_files_one_id_flagged

### AC3: Non-zero exit on collision

- **Given** at least one duplicate ID exists
- **When** `next_id.py collisions` runs
- **Then** it exits non-zero (the release-gate signal), and exits 0 when clean
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_duplicate_id.py::ExitTests::test_nonzero_exit_on_collision

### AC4: Machine-readable output

- **Given** a collision
- **When** the detector runs
- **Then** it returns `{ "duplicates": [ { "id", "files": [...] } ], "count" }`, sorted deterministically
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_duplicate_id.py::OutputTests::test_json_shape

## Implementation

`next_id.py` `collisions` subcommand plus a `detect_collisions(repo_root)` helper (pure stdlib); six tests in `test_duplicate_id.py`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint loop | Decomposed from CR0002, implemented under TDD, verified, critic APPROVE |
| 2026-06-20 | Darren Benson | Restored after a status-flip script truncated the file (footgun: open in write mode before the read) |
