# US0601: review.signoff is operator by default and panel only by explicit config, so no consuming project silently loses its human

> **Status:** Done
> **Closed with findings in:** repaired in 307ce91d - the output states panel sign-off is in force
> **Delivers:** CR0514
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0198
> **Points:** 3

## User Story

**As a** maintainer of a consuming project
**I want** panel sign-off to be opt-in and off by default
**So that** no project loses its human reviewer without somebody deciding to

## Acceptance Criteria

### AC1: the default is operator

- **Given** a project with no `review.signoff` setting
- **When** a sign-off is attempted by a panel
- **Then** it is refused, because the independence bar must not change under a project during an upgrade
- **Verify:** manual - retired by US0919: `review.signoff` is retired; the operator signs the run once at `sprint sign`
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

### AC2: panel is reached only by explicit config

- **Given** `review.signoff: panel` recorded in `.config.yaml`
- **When** the panel signs
- **Then** it is accepted, and the output states that panel sign-off is in force
- **Verify:** manual - retired by US0919: `review.signoff` is retired; the operator signs the run once at `sprint sign`
- **Verified:** manual (2026-09-25) - retired, superseded by US0919

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | US0919 | AC1 and AC2 retired in the D0259 pattern: `review.signoff` is retired; the operator signs the run once at `sprint sign` |
