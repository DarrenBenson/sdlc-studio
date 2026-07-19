# US0242: switch README, docs and the SKILL description off review generate to audit --profile repo

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** README.md, docs/why-sdlc-studio.md, docs/existing-users.md, .claude/skills/sdlc-studio/SKILL.md
> **Epic:** EP0078
> **Points:** 2

## User Story

**As a** newcomer following the README's zero-setup on-ramp
**I want** every public surface to send me to `audit --profile repo`
**So that** no shipped instruction lands me on a command that no longer exists

## Acceptance Criteria

### AC1: No public surface still names the retired command

- **Given** `README.md` (two references), `docs/why-sdlc-studio.md`, `docs/existing-users.md` and the SKILL.md description all say `review generate`
- **When** those surfaces are searched for the retired name
- **Then** nothing matches, in prose or in a command example
- **Verify:** shell ! grep -rn "review generate" README.md docs .claude/skills/sdlc-studio/SKILL.md
- **Verified:** yes (2026-07-19)

### AC2: All four surfaces name the replacement

- **Given** the same four files, each of which carried the on-ramp
- **When** each is searched for the new name
- **Then** all four carry `audit --profile repo`, so the on-ramp is redirected rather than merely deleted
- **Verify:** shell test $(grep -l "audit --profile repo" README.md docs/why-sdlc-studio.md docs/existing-users.md .claude/skills/sdlc-studio/SKILL.md | wc -l) -eq 4
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
