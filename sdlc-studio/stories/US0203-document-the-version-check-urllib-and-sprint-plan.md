# US0203: Document the version-check urllib and sprint-plan git-fetch network surface in the PRD Security NFR and TRD rule 6/threat table

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As a** reader of the PRD and TRD
**I want** the version-check and sprint-plan git-fetch network calls enumerated in the Security NFR and threat table
**So that** every outbound network path the skill makes is declared rather than discovered

## Acceptance Criteria

### AC1: PRD Security NFR and Section 8 integration map enumerate the version check (direct HTTPS to

- **Given** the PRD Security NFR and §8 named only `gh` as a network path
- **When** the version check and git fetch are enumerated in both
- **Then** PRD Security NFR and Section 8 integration map enumerate the version check (direct HTTPS to api.github.com, default-on, `version_check.enabled` opt-out, silent-failure semantics) and sprint plan's git fetch origin
- **Verify:** grep "reach the network on these outbound, optional paths only" sdlc-studio/prd.md
- **Verified:** yes (2026-07-17)

### AC2: The version check appears in the PRD feature inventory

- **Given** the version check had no PRD feature-inventory row
- **When** a Skill self-update / version check row is added
- **Then** The version check appears in the PRD feature inventory
- **Verify:** grep "Skill self-update / version check" sdlc-studio/prd.md
- **Verified:** yes (2026-07-17)

### AC3: trd.md rule 6 and the §9 threat/controls rows bound the network to the paths §5 Network paths lists

- **Given** trd rule 6 said "no network access except the gh CLI wrapper"
- **When** rule 6 and the §9 rows are rewritten to name all three paths
- **Then** trd.md rule 6 limits network access to the outbound paths §5 Network paths lists and names the three mechanisms it bounds (calling `gh`, opening a connection through `urllib`, running `git fetch`); that table gives each path its trust boundary in its `Under ADR-004` column; and in §9 the Network exfiltration threat row points at that table while the Encryption in transit control names `gh`, the `api.github.com` release check and `git fetch origin`
- **Verify:** grep "Network access is limited to the outbound paths" sdlc-studio/trd.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 | BG1176: AC1's Verify re-pointed at "reach the network on these outbound, optional paths only", the sentence US1104 (8f380767) wrote in place of the one the old grep read; its text still holds. AC3's Verify re-pointed at "Network access is limited to the outbound paths", the rule 6 sentence US1101 (0f26c3e8) wrote. AC3's heading and Then reworded: rule 6 now points at a five-row Network paths table, three of its rows `gh` callers, rather than naming three paths |
