# US0108: Version and CHANGELOG conversion to 4.0.0-rc.1 and dormant-schema banner removal

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0024
> **Persona:** Engineering seat
> **Affects:** CHANGELOG.md, templates/version.yaml, README.md, sdlc-studio/reviews/LATEST.md, tools/check_versions.py
> **Depends on:** US0105, US0106, US0107

## User Story

**As a** maintainer preparing the rc tag
**I want** the version strings homed at `4.0.0-rc.1`, the CHANGELOG `[Unreleased]` converted to the 4.0.0 sections, and the dormant-schema-v3 / freeze banners removed
**So that** the tree describes the v4 rc state consistently and `check_versions` enforces it

Delivers CR0198 item 4. Lands locally; the tag/push stays operator-gated (US0109).

## Acceptance Criteria

### AC1: version strings home at 4.0.0-rc.1 and check_versions passes

- **Given** the authoritative version files
- **When** `check_versions` runs
- **Then** every authoritative file reads `4.0.0-rc.1` and the guard passes
- **Verify:** shell python3 tools/check_versions.py
- **Verified:** yes (2026-07-09)

### AC2: the CHANGELOG [Unreleased] block is converted to 4.0.0 sections

- **Given** `CHANGELOG.md`
- **When** it is read
- **Then** the `[Unreleased]` content is under a `## [4.0.0]` heading (breaking-change inventory named)
- **Verify:** grep "## \[4.0.0\]" CHANGELOG.md
- **Verified:** yes (2026-07-09)

### AC3: the dormant-schema-v3 / freeze banners are removed

- **Given** CHANGELOG.md, LATEST.md and README.md
- **When** they are read
- **Then** the pre-v4 "ships dormant behind schema_version: 3" / "release freeze until v4.0" banners are gone (they describe the superseded state)
- **Verify:** shell test -z "$(grep -rl 'release freeze until v4' CHANGELOG.md README.md sdlc-studio/reviews/LATEST.md)"
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0198 item 4 (version + banner sweep) |
