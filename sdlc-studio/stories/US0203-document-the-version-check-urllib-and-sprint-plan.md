# US0203: Document the version-check urllib and sprint-plan git-fetch network surface in the PRD Security NFR and TRD rule 6/threat table

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: PRD Security NFR and Section 8 integration map enumerate the version check (direct HTTPS to

- **Given** the PRD Security NFR and §8 named only `gh` as a network path
- **When** the version check and git fetch are enumerated in both
- **Then** PRD Security NFR and Section 8 integration map enumerate the version check (direct HTTPS to api.github.com, default-on, `version_check.enabled` opt-out, silent-failure semantics) and sprint plan's git fetch origin
- **Verify:** grep "four outbound, optional paths" sdlc-studio/prd.md
- **Verified:** yes (2026-07-17)

### AC2: The version check appears in the PRD feature inventory

- **Given** the version check had no PRD feature-inventory row
- **When** a Skill self-update / version check row is added
- **Then** The version check appears in the PRD feature inventory
- **Verify:** grep "Skill self-update / version check" sdlc-studio/prd.md
- **Verified:** yes (2026-07-17)

### AC3: trd.md rule 6 and the §9 threat/controls rows name all three network paths (gh wrapper, version

- **Given** trd rule 6 said "no network access except the gh CLI wrapper"
- **When** rule 6 and the §9 rows are rewritten to name all three paths
- **Then** trd.md rule 6 and the §9 threat/controls rows name all three network paths (gh wrapper, version check urllib, git fetch) with their trust boundaries
- **Verify:** grep "Network access is limited to three outbound paths" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
