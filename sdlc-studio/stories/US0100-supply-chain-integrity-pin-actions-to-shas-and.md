# US0100: Supply-chain integrity: pin Actions to SHAs and verify installer checksums

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0022
> **Persona:** Engineering seat
> **Affects:** .github/workflows, install.sh, tools/check_action_pins.sh

## User Story

**As a** maintainer wary of a compromised third-party Action or a tampered install tarball
**I want** every GitHub Action pinned to a full commit SHA and both installers to verify a per-release checksum before extraction
**So that** a moved tag or a swapped artefact cannot inject code into CI or a consumer's install

Delivers CR0186 items 1-2 (defence-in-depth, remediation-only).

## Acceptance Criteria

### AC1: Every GitHub Action is pinned to a full commit SHA

- **Given** the workflow files under `.github/workflows/`
- **When** they are inspected
- **Then** every `uses:` third-party Action references a 40-hex commit SHA (with the version in a trailing comment), not a mutable `@vN`/branch tag; CI stays green
- **Verify:** shell test -z "$(grep -rhoE 'uses: [^@]+@[^ ]+' .github/workflows | grep -vE '@[0-9a-f]{40}')"

### AC2: Both installers verify a per-release checksum before extraction

- **Given** `install.sh` (and any second installer path)
- **When** it fetches a release artefact
- **Then** it verifies the artefact against a published per-release checksum (sha256) and aborts on mismatch, before any extraction
- **Verify:** grep -iE "sha256|shasum" install.sh

### AC3: A guard keeps the pins from regressing

- **Given** a new `tools/check_action_pins.sh` (or an extension of an existing guard)
- **When** it runs in the gate
- **Then** it fails if any Action reverts to a tag/branch ref, so the pin cannot silently rot
- **Verify:** shell bash tools/check_action_pins.sh

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0186 (supply-chain items) |
