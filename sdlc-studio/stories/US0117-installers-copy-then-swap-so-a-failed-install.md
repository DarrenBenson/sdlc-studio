# US0117: Installers copy-then-swap so a failed install cannot destroy the previous one

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new
> **Epic:** EP0027
> **Persona:** first-run operator (dogfooding)
> **CR:** CR0205

## User Story

**As a** person installing or refreshing the skill
**I want** a failed copy to leave my existing install untouched
**So that** a disk-full, permission, or interrupted install never leaves me with nothing

## Context

RV0007: `install.sh` did `rm -rf "$dest"; cp -r ...`. Between the delete and a completed copy
(disk full, permission error, Ctrl-C), the user's only copy of the skill is gone or half-copied.
Both the install and the sweep-refresh paths share the defect.

## Acceptance Criteria

### AC1: a failed copy leaves the previous install byte-for-byte intact

- **Given** an existing install at `$dest` and a `cp` that fails
- **When** `install_to` runs
- **Then** the previous install is unchanged and the function reports failure (non-zero)
- **Verify:** pytest tools/tests/test_install_atomic.py -k failed_copy
- **Verified:** yes (2026-07-10)

### AC2: a successful install still replaces cleanly

- **Given** a working `cp`
- **When** `install_to` runs over an existing install
- **Then** the new content replaces the old and the changelog is shipped
- **Verify:** shell bash -n install.sh
- **Verified:** yes (2026-07-10)

### AC3: the sweep-refresh path uses the same safe swap

- **Given** the stale-copy sweep refreshes another install
- **When** the copy fails
- **Then** that install is left at its old version, not destroyed
- **Verify:** grep -q "swap_install" install.sh
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
| 2026-07-10 | sprint (CR0205 decomposition) | ACs authored from the RV0007 finding; copy-then-swap |
