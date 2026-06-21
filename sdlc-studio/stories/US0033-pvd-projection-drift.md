# US0033: read-only PVD projection + drift check

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0048)
> **Reviewer:** --
> **Created:** 2026-06-21
> **GitHub Issue:** --

## User Story

**As a** multi-repo product team
**I want** the master PVD projected into each repo read-only, with drift detection
**So that** every repo sees one true vision and a stale/edited copy is caught (RFC0015 WS2).

## Acceptance Criteria

### AC1: sync projects a read-only copy, idempotently

- **Given** a master PVD and a target repo
- **When** `sync` runs (copy or symlink)
- **Then** the projection is read-only, matches the master, and a second sync replaces it without error
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_pvd.py::SyncTests
- **Verified:** yes (2026-06-21)

### AC2: drift distinguishes in-sync / stale / behind / missing, never vacuous in-sync

- **Given** a projected copy
- **When** `drift` compares it to the master
- **Then** it reports in-sync / stale / behind / missing, and an unreadable/missing master reports error (not a false in-sync)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_pvd.py::DriftTests
- **Verified:** yes (2026-06-21)

### AC3: symlink mode + manifest parse (inline comments stripped)

- **Given** symlink mode and a product manifest
- **When** sync uses symlink and `read_manifest` parses the manifest
- **Then** the symlink resolves to the master and manifest values carry no inline-comment cruft
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_pvd.py::SymlinkModeTests
- **Verified:** yes (2026-06-21)

## Implementation

`scripts/pvd.py` (`sync` read-only copy/symlink, idempotent; `drift` sha256+version with an
error guard on an unreadable master; `read_manifest` strips inline comments);
reference-scripts.md entry. Workflow in reference-pvd.md / help/pvd.md (CR0047).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0048) | Decomposed from CR0048 (RFC0015 WS2); critic REJECT->fixed (vacuous in-sync on unreadable master, manifest inline comments) |
