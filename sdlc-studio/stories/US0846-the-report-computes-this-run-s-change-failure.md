# US0846: the report computes this run's change failure rate from its own push-triggered CI results, so a narrowed gate can be judged against it

> **Status:** Draft
> **Created:** 2026-09-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0255
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator judging whether a cheaper gate cost anything
**I want** this run's change failure rate computed from its own deploys, beside the elite band
**So that** narrowing a gate is judged against the rate it might have raised, rather than on faith

## Acceptance Criteria

Three of the next batch's four epics make a gate cheaper and one removes a control, against a measured 33% change failure rate. The rate has to be in the report for that trade to be judgeable, and it has to be derived from the run's own deploys rather than typed.

### AC1: the rate is derived from the run's push-triggered CI results, and names the mapping it used

- **Given** a run whose window holds three pushes to main, one of whose push-triggered Lint runs concluded failure
- **When** the report is produced
- **Then** its DORA section carries `33%` with the deploy count, the failed sha, and the mapping stated - that a push to main IS the deployment in a trunk-based repository with no separate deploy step
- **Mutant:** count every CI run in the window rather than push-triggered ones alone - a dispatch or a schedule then counts as a deployment, and this run's rate reads 20% instead of 33%
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DoraTests::test_change_failure_rate_counts_push_triggered_runs_only

### AC2: a run whose deploys cannot be read says so, and never prints a rate

- **Given** a run whose window holds no push-triggered run, or a forge that cannot be reached
- **When** the report is produced
- **Then** the key reads `NOT MEASURED` with the reason, and no percentage is shown
- **Mutant:** render 0% when the list is empty - a run nobody could measure then reads as a run with no failures, which is the direction this project has already been burned in
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DoraTests::test_an_unreadable_deploy_set_is_not_zero_percent

### AC3: the rate is recorded per run so the next one can be compared with it

- **Given** two consecutive runs with reports
- **When** the second is produced
- **Then** it carries the previous run's rate beside its own, from the recorded figure rather than a re-derivation of a closed run
- **Mutant:** re-derive the previous run's rate at report time - a closed run's window can no longer be read reliably, so the comparison silently becomes two different measurements
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::DoraTests::test_the_previous_runs_rate_is_read_not_rederived

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-17 | sdlc-studio | Created via `new` (deterministic) |
