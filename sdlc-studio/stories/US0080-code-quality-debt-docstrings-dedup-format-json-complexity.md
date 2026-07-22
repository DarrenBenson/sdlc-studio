# US0080: Code-quality debt: docstrings, dedup, format json, complexity

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0018
> **Persona:** Skill Maintainer
> **Source:** CR-0187

## User Story

**As a** skill maintainer
**I want** the RV0006 code-quality debt cleared
**So that** stale docstrings, duplicated primitives and complexity hotspots stop inviting the next defect

## Acceptance Criteria

### AC1: Accurate docs, shared primitives, even JSON

- **Given** the flagged sites
- **When** cleaned up
- **Then** the reconcile docstring lists all four subcommands, find_by_id/linked_to_epic live in
  lib and the duplicates delegate, and apply/revision/rebuild accept --format json
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py -k format_json
- **Verified:** yes (2026-07-10)

### AC2: Hotspots decomposed, latent issues fixed

- **Given** the four named complexity hotspots and the test-suite issues
- **When** refactored
- **Then** they are decomposed with no behaviour change, the raw-string escape is fixed, and
  `.local` logs roll with an opt-in SDLC_DEBUG channel
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
- **Verified:** yes (2026-07-22)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
