# US0499: The close reports execution actuals against the declared policy, so a sprint that ran the suite fifty times shows it

> **Status:** Review
> **Delivers:** CR0453
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator reading a retro that says the sprint went well
**I want** the close to report how many full-suite runs happened and what they cost
**So that** a sprint that spent three hours re-running tests shows it, instead of reporting only what was delivered

## Acceptance Criteria

### AC1: the close reports execution actuals against the declared policy

- **Given** a run whose strategy declared a policy
- **When** the close runs
- **Then** it reports the number of full-suite runs, the selected runs and their cost, set against what the policy declared
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ExecutionActualsTests::test_the_close_reports_runs_against_the_policy

### AC2: an unmeasured cost is reported as unmeasured, never as zero

- **Given** a run with no recorded execution data
- **When** the close runs
- **Then** it says the cost was not captured and why, rather than printing a total that reads as cheap
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ExecutionActualsTests::test_an_unmeasured_cost_is_not_reported_as_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
