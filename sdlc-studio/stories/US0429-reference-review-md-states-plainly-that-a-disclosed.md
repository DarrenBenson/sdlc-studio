# US0429: reference-review.md states plainly that a disclosed sign-off is not an independent one, and what that costs

> **Status:** Done
> **Delivers:** RFC0051
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md
> **Epic:** EP0159
> **Points:** 2

## User Story

**As a** reader of reference-review.md
**I want** it stated plainly that a disclosed sign-off is not an independent one
**So that** the guard is not read as proving the property its name claims

## Acceptance Criteria

### AC1: the cost of a disclosed sign-off is stated plainly

- **Given** reference-review.md
- **When** a reader asks what a delegated sign-off proves
- **Then** it carries a `## A disclosed sign-off is not an independent one` section stating that the guard no longer proves the property its name claims, and that the audit trail's value rests on the disclosure being read
- **Verify:** manual - retired by US0924: per-unit sign-off was retired in v6, and with it the delegated sign-off and its disclosure marker this section weighed; the run is signed once at `sprint sign`, and reference-review.md no longer carries the section
- **Verified:** manual (2026-09-27) - retired, superseded by US0924

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | Claude Opus 5.5 | AC1 retired by US0924 (D0259 pattern): the delegated per-unit sign-off it documented was retired in v6, so the section is deleted from reference-review.md |
