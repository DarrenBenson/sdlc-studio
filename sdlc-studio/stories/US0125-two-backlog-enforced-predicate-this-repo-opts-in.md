# US0125: two_backlog_enforced predicate + this repo opts in

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, sdlc-studio/.config.yaml
> **Epic:** EP0034
> **Points:** 2

## User Story

**As an** operator upgrading an existing project to this skill
**I want** the hard two-backlog gates to be enforce-on-request, defaulting off
**So that** my existing CR workflow keeps working until I explicitly opt in, and only the projects that turned it on get the gates.

## Acceptance Criteria

### AC1: enforcement defaults off and opts in via one config line

- **Given** a project with no `two_backlog.enforce` config, and one that sets it `true`
- **When** `sdlc_md.two_backlog_enforced(root)` is read
- **Then** it is False by default (upgrade-safe) and True when the config opts in; an explicit `false` stays off
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::EnforcementGateTests
- **Verified:** yes (2026-07-15)

### AC2: this repo opts in, so its own gates stay on

- **Given** this repo dogfoods the two-backlog workflow
- **When** its `.config.yaml` is read
- **Then** `two_backlog.enforce` is `true`, so `two_backlog_enforced` is True here despite the default-off
- **Verify:** shell python3 -c "import sys; sys.path.insert(0,'.claude/skills/sdlc-studio/scripts'); from lib import sdlc_md; assert sdlc_md.two_backlog_enforced('.') is True"
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
