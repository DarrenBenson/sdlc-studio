# US0338: A fit is never applied automatically: the plan states how many sprints it rests on and refuses to publish a fitted fixed term below a stated minimum

> **Status:** Done
> **Delivers:** CR0391
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0114
> **Points:** 3

## User Story

**As an** operator reading a plan that quotes a fixed per-sprint cost
**I want** the plan to state how many sprints the fit rests on, and to refuse to apply one
resting on fewer than a stated minimum
**So that** a line drawn through two points is never spent as though it were calibration

## Context

CR0391's own fit rests on two sprints, and two points always fit a straight line exactly. The
estimator has been burned twice by refitting to one or two observations, which is why
`RATE_MIN_UNITS` exists on the marginal side. This story is the same discipline on the fixed
side: report the candidate, name what it rests on, and do not spend it until the record earns
it.

## Acceptance Criteria

### AC1: a fit below the minimum is reported but never enters the total

- **Given** a velocity record with fewer qualifying whole-sprint rows than the stated minimum,
  for example the two of CR0391's own fit
- **When** a plan is built
- **Then** the forecast total does not include the fitted fixed term, and the plan reports the
  candidate fit as NOT APPLIED, naming the minimum required and the count the project has - a
  total that moved the moment a second row landed fails this
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AFitIsNeverAppliedAutomaticallyTests::test_a_two_sprint_fit_is_reported_and_kept_out_of_the_total
- **Verified:** yes (2026-07-23)

### AC2: no fixed term is ever quoted without the number of sprints behind it

- **Given** any plan whose forecast quotes a fixed per-sprint term, applied or not
- **When** the forecast is rendered
- **Then** the sprint count the term was fitted from appears beside the figure, so no reader
  can take the number without its sample size
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AFitIsNeverAppliedAutomaticallyTests::test_every_quoted_fixed_term_states_the_sprint_count_behind_it
- **Verified:** yes (2026-07-23)

### AC3: at or above the minimum the fit is applied, and the plan says so

- **Given** a record carrying at least the minimum number of qualifying sprints
- **When** a plan is built
- **Then** the fixed term enters the total and the plan states it was applied on that many
  sprints, so the refusal is a threshold the evidence can clear and not a permanent no
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AFitIsNeverAppliedAutomaticallyTests::test_a_fit_at_the_minimum_is_applied_and_names_its_sprint_count
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
