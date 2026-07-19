# US0267: A unit close names the fields that unit type requires before its terminal transition, ahead of the work rather than on refusal

> **Status:** Done
> **Delivers:** CR0361
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0086
> **Points:** 3

## User Story

**As an** agent delivering a unit
**I want** to be told what its terminal transition will require before I start
**So that** the requirement is met as part of the work rather than discovered as a refusal after it

## Context

Five `Verification depth` refusals in one session, each after the work was complete.

The sharper problem, found while grooming this story and filed as **BG0213**: the one pre-flight
that exists gives the WRONG answer. `transition set --dry-run` does not evaluate the transition
gates, so a bug with no `Verification depth` field is reported as `would set BG0001 Open -> Fixed`
while the real run blocks it. A dry-run that disagrees with the real run is worse than none - it
is the false-completeness class this project keeps finding, not merely a missing feature.

The requirement functions already exist and return a reason string or `None`
(`transition._depth_gate` and its siblings). A reporter must call THOSE, not restate them, or the
pre-flight becomes a second copy that drifts from the guard it describes - CR0361's own third
acceptance criterion.

## Acceptance Criteria

### AC1: a dry-run reports every refusal the real run would hit

- **Given** a unit that fails a terminal-transition requirement
- **When** `transition set --dry-run` is invoked for that transition
- **Then** it reports the same refusal the real run gives, and changes nothing (BG0213)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k DryRunHonestyTests
- **Verified:** yes (2026-07-19)

### AC2: the dry-run and the real run never disagree

- **Given** any unit and any target status
- **When** both paths are evaluated
- **Then** they agree on whether the transition is allowed; the only difference is whether the
  write happens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k test_the_dry_run_and_the_real_run_agree
- **Verified:** yes (2026-07-19)

### AC3: the requirements are derived from the gate functions, not restated

- **Given** the pre-flight reporter
- **When** a transition requirement changes in the gate
- **Then** the reported text changes with it, because the reporter calls the same function - a
  test fails if the reporter carries its own copy of a requirement string
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k test_requirements_are_not_duplicated
- **Verified:** yes (2026-07-19)

### AC4: a unit's requirements can be asked for before the work

- **Given** a unit id and its intended terminal status
- **When** the agent asks what that transition will require
- **Then** the unmet requirements are listed by name, with nothing written
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k test_requirements_listed_before_work
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Groomed: ACs anchored on BG0213, found while grooming this story |
