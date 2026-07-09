# US0101: Sync, state and verifier-sandbox hardening

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0022
> **Persona:** Engineering seat
> **Affects:** scripts/github_sync.py, scripts/verify_ac.py, scripts/mutation.py, .gitignore, scripts/tests/test_github_sync.py, scripts/tests/test_verify_ac.py

## User Story

**As a** maintainer running sync and executable-AC verification against untrusted content
**I want** `github_sync` push to refuse to leak a secret, local state kept out of git, and the restricted `http` verb + mutation `--test` boundary enforced/documented
**So that** a secret in a CR body, a committed state file, or an over-broad verifier cannot cause harm

Delivers CR0186 items 3-5.

## Acceptance Criteria

### AC1: github_sync push scans for secrets and defaults safe on a public target

- **Given** a `github_sync push` whose payload contains a secret-shaped token
- **When** the target repo is public
- **Then** the push scans for secrets and refuses (or defaults to dry-run / requires explicit confirmation) rather than publishing it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py::SecretScanTests

### AC2: Local state stays out of git

- **Given** the repo's ignore rules
- **When** a run writes `version-check.json` or a skill-install `.local/`
- **Then** both are gitignored / untracked so machine-local state never lands in a commit
- **Verify:** shell git check-ignore -q sdlc-studio/.local/version-check.json || grep -qE "version-check.json|\.local/" .gitignore

### AC3: The restricted http verb enforces scheme/host limits

- **Given** a verifier using the `http` verb under restricted mode
- **When** it targets a scheme/host outside the allow-list
- **Then** it is refused; the mutation `--test` boundary is documented alongside
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RestrictedHttpTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0186 (sync/state/verifier items) |
