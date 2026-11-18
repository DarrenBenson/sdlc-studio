# US1234: A command derives change failure rate from release records and linked incidents, never reading 0% unmeasured

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0695
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/help/deploy.md, .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py
> **Epic:** EP0339
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A command derives change failure rate from release records and linked incidents, never reading 0% unmeasured
**So that** CR0695 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The command states the rate with the releases counted and the window

- **Given** four settled release records in the window, one of them the `Shipped-in` release of an escaped bug that an incident issue with a root-cause section was triaged into
- **When** the change failure rate command of `escape.py` is run
- **Then** it prints 25%, names the four releases counted, the one that failed with its incident's id, and the window's two dates. Fails on: a bare percentage, or a release counted as failed for a bug no incident names
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py::ChangeFailureRateTests::test_the_rate_names_the_releases_counted_the_incident_and_the_window

### AC2: A release inside the settling period is pending

- **Given** the same records and a fifth release younger than the settling period
- **When** the command is run
- **Then** the fifth release is listed as pending with the period stated, and is in neither the releases counted nor the failed ones, so the rate is still one in four. Fails on: a young release counted as a success, which lowers the rate before an incident could be linked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py::ChangeFailureRateTests::test_a_release_younger_than_the_settling_period_is_pending

### AC3: No release or no incident record reads not measured, never 0%

- **Given** one project with no release record in the window, a second with releases and no incident issue at all, and a third with releases and an incident issue linked to none of them
- **When** the command is run in each
- **Then** the first two print 'not measured: <reason>' naming what is absent and no percentage, and the third prints 0% naming the releases counted. Fails on: 0% for a project that records no incidents, or 'not measured' where incidents are recorded and none is linked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py::ChangeFailureRateTests::test_no_release_or_no_incident_record_reads_not_measured

### AC4: The help names the command and how its rate differs from the CI one

- **Given** `help/deploy.md`
- **When** its commands table is read
- **Then** it names the command, its settling period and its source records, and says it counts releases with a linked incident where `deploy.py metrics` counts failed deploys in the ledger. Fails on: help that leaves two figures called change failure rate with nothing to tell them apart
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_change_failure_rate.py::ChangeFailureRateTests::test_the_deploy_help_names_the_command_and_its_sources

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
