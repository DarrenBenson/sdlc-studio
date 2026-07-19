# US0243: update help/review, help/audit and the catalogue; check_links and validate_skill green

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/review.md, .claude/skills/sdlc-studio/help/audit.md
> **Epic:** EP0078
> **Points:** 2

## User Story

**As an** agent reading the help to pick a command
**I want** the help pages and the catalogue to describe one weakness-hunt under one name
**So that** I cannot reach a retired route through a stale help row or a dead link

## Acceptance Criteria

### AC1: help/review.md is the consistency job only

- **Given** `help/review.md` documents the repository-review on-ramp alongside the unified PRD/TRD/TSD pass, and `help/help.md` carries its catalogue row
- **When** both pages are searched for the retired command
- **Then** neither mentions it: the on-ramp section and its catalogue row are gone, and what remains is the consistency review
- **Verify:** shell ! grep -n "review generate" .claude/skills/sdlc-studio/help/review.md .claude/skills/sdlc-studio/help/help.md
- **Verified:** yes (2026-07-19)

### AC2: help/audit.md and the catalogue carry the repo profile

- **Given** `help/audit.md` lists only the project and skill profiles today
- **When** a reader looks for the zero-setup path on an existing repo
- **Then** `help/audit.md` documents the repo profile and its three legs, and the `help/help.md` catalogue row names the same invocation
- **Verify:** shell grep "audit --profile repo" .claude/skills/sdlc-studio/help/audit.md && grep "audit --profile repo" .claude/skills/sdlc-studio/help/help.md
- **Verified:** yes (2026-07-19)

### AC3: Link graph and skill spec stay green

- **Given** the edited help pages cross-reference `reference-audit.md` anchors and the pack the removal replaced them with
- **When** the link guard runs over the tree and `help/audit.md` is checked for that cross-reference
- **Then** no anchor points at a deleted section or file, and the audit help links the repo pack rather than describing it in prose alone
- **Verify:** shell python3 tools/check_links.py && grep "audit-profiles/repo.md" .claude/skills/sdlc-studio/help/audit.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
