# US0335: A carried-forward finding is linked to the units it was found against, so it cannot be lost when the sprint closes

> **Status:** Draft
> **Depends on:** US0332
> **Delivers:** CR0404
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py
> **Epic:** EP0113
> **Points:** 2

## User Story

**As a** maintainer picking up a carried finding weeks later
**I want** it to name the units it was found against
**So that** it cannot become an orphan bug nobody can place once the sprint that produced it
is closed

## Acceptance Criteria

### AC1: a carried finding names the units it was found against

- **Given** a finding filed under carry-forward against two units of the batch
- **When** it is written
- **Then** it carries both unit ids, and a finding naming none is refused rather than filed
  unattached
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::CarriedFindingLinkTests::test_a_carried_finding_naming_no_unit_is_refused

### AC2: the link survives the close of the sprint that produced it

- **Given** a carried finding whose sprint has closed and whose units have gone terminal
- **When** the finding is read
- **Then** it still resolves to those units, so closing the run does not strand it - the
  failure mode the goal verdict already demonstrates, where a judgement outlives the state
  that explains it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::CarriedFindingLinkTests::test_a_carried_finding_still_resolves_after_its_sprint_closes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
