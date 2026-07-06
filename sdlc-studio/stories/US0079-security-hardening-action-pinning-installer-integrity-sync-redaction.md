# US0079: Security hardening: action pinning, installer integrity, sync redaction

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0018
> **Persona:** Skill Maintainer
> **Source:** CR-0186

## User Story

**As a** security-conscious maintainer
**I want** the RV0006 defensive-security hardening debt cleared
**So that** the supply chain and state hygiene match the tool's own standards

## Acceptance Criteria

### AC1: Supply-chain and integrity hardening

- **Given** CI actions and the installers
- **When** hardened
- **Then** actions are SHA-pinned, both installers verify a per-release checksum before extraction,
  and the skill-install `.local/` is gitignored (version-check.json untracked)
- **Verify:** python3 tools/tests then discover the action-pinning guard

### AC2: Sync redaction and verifier limits

- **Given** a public target repo and restricted-mode verify
- **When** github_sync pushes and verify_ac runs
- **Then** push scans for secrets and requires confirmation, and the http verb enforces scheme/host limits
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py -k redact

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
