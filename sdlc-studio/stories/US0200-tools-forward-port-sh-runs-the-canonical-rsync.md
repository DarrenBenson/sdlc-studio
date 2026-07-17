# US0200: tools/forward-port.sh runs the canonical rsync dry-run by default with --yes to apply, refusing a reversed direction or non-dev-repo cwd; AGENTS.md references it

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/forward-port.sh, AGENTS.md
> **Epic:** EP0070
> **Points:** 2

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the dev-repo-to-installed-copy rsync as a checked-in, guarded one-liner
**So that** a hand-typed --delete without the .local exclude can never destroy the installed copy's state

## Acceptance Criteria

### AC1: the script is guarded and dry-run by default

- **Given** the dev repo as cwd, an installed copy target, and separately a reversed or non-dev-repo invocation
- **When** `tools/forward-port.sh` runs with and without `--yes`
- **Then** The script runs the canonical rsync with the exact exclusions, dry-run by default, --yes to apply; reversed direction or a non-dev-repo cwd is refused
- **Verify:** shell python3 -m unittest discover -s tools/tests -p test_forward_port.py
- **Verified:** yes (2026-07-17)

### AC2: AGENTS.md points at the script

- **Given** the repository guidance file
- **When** the forward-port note is read
- **Then** AGENTS.md's forward-port note references the script instead of an inline rsync incantation
- **Verify:** grep "forward-port.sh" AGENTS.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
