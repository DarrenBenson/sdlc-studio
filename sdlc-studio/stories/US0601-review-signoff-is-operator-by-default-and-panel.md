# US0601: review.signoff is operator by default and panel only by explicit config, so no consuming project silently loses its human

> **Status:** Ready
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
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffPolicyTests::test_the_default_is_operator

### AC2: panel is reached only by explicit config

- **Given** `review.signoff: panel` recorded in `.config.yaml`
- **When** the panel signs
- **Then** it is accepted, and the output states that panel sign-off is in force
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffPolicyTests::test_panel_is_reached_only_by_explicit_config

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
