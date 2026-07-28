# US0536: The guidance states the fragment path as the rule for a lane, so an author following it cannot collide with a sibling

> **Status:** Review
> **Delivers:** CR0467
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md
> **Epic:** EP0183
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** an agent working in a parallel delivery lane
**I want** the guidance to name the changelog fragment as the rule for a lane
**So that** following the documented path does not collide with a sibling lane or get me refused

## Acceptance Criteria

### AC1: the guidance names the fragment path as the rule for a lane

- **Given** the doctrine's changelog guidance
- **When** an author working in a parallel lane follows it
- **Then** it directs them to write a fragment, and the [Unreleased] instruction is scoped to the release step rather than stated as the general rule
- **Verify:** grep -n 'fragment' .claude/skills/sdlc-studio/reference-doctrine.md
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
