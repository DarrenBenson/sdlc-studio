# US0119: Reliability debt batch: atomic-write perms, atomic .local state, sync/scale hardening

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new
> **Epic:** EP0027
> **Persona:** repo maintainer (dogfooding)
> **CR:** CR0207

## User Story

**As a** maintainer relying on the deterministic tooling
**I want** the Low-severity reliability debt from RV0007 cleared in one batch
**So that** the small crash/perms/scale hazards stop accumulating

## Context

RV0007 consolidated ~14 Low reliability findings into CR0207. This story actions the
mechanically-clear, high-value subset; a residual list is recorded in the CR for a follow-up.

## Acceptance Criteria

### AC1: atomic_write preserves file permissions

- **Given** a 0664 file
- **When** `atomic_write` replaces it
- **Then** the mode stays 0664 (not silently flipped to mkstemp's 0600)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_concurrency.py -k atomic_write_preserves_mode
- **Verified:** yes (2026-07-10)

### AC2: .local guardrail state is written atomically

- **Given** loop_guard and resume state writers
- **When** they persist state
- **Then** they route through `sdlc_md.atomic_write` (a crash mid-write cannot reset the guard)
- **Verify:** shell grep -q atomic_write .claude/skills/sdlc-studio/scripts/loop_guard.py
- **Verified:** yes (2026-07-10)

### AC3: the http verb refuses a scheme-less URL in every mode

- **Given** a `Verify: http GET example.com/x` (no scheme)
- **When** the command is built
- **Then** it is refused (not passed to curl to guess the protocol)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k build_command_http
- **Verified:** yes (2026-07-10)

### AC4: hardening one-liners land (watermark, timeouts, npx, guards)

- **Given** the batch of small fixes
- **When** applied
- **Then** the cascade watermark uses max(mergedAt), next_id ls-tree has a timeout, npx jest runs with --no-install, check_neutrality fails loud, the em-dash guard is grep-P-free, and install.ps1 ships the CHANGELOG
- **Verify:** shell grep -q "max((pr.get" .claude/skills/sdlc-studio/scripts/github_sync.py
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
| 2026-07-10 | sprint (CR0207 decomposition) | ACs authored; actionable subset of the themed debt |
