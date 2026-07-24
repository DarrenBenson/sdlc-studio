# US0431: a design rung's close reports how many units it groomed, so an accepted-but-ungroomed batch cannot close silently

> **Status:** Ready
> **Delivers:** CR0418
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0160
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a design rung's close reports how many units it groomed

- **Given** a design rung closing over a batch it groomed
- **When** the close runs
- **Then** it states how many units were groomed and how many remain ungroomed - the counterweight D0062 requires, without which the gate's relaxation is a blanket escape
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GroomingReportTests::test_the_close_reports_the_grooming_it_produced

### AC2: a design rung that groomed nothing cannot close silently

- **Given** a design rung whose batch is as ungroomed at the close as it was at the plan
- **When** the close runs
- **Then** that is reported prominently rather than passing as an ordinary close - accepting an ungroomed batch and grooming none of it is exactly the abuse the relaxation invites
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GroomingReportTests::test_a_rung_that_groomed_nothing_is_reported_not_passed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
