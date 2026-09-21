# US0866: the sprint plan records its operational design domain: the files it may touch, the artefacts it may create, the statuses it may set and the budget it may spend

> **Status:** Draft
> **Delivers:** RFC0060
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0259
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the sprint plan records its operational design domain: the files it may touch, the artefacts it may create, the statuses it may set and the budget it may spend
**So that** RFC0060 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1: the plan records a boundary derived from the batch.**
  - **Given** a batch whose units declare `Affects` across three files
  - **When** `sprint plan --write` runs
  - **Then** run state records an operational design domain carrying those files and the artefact types those units touch
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OperationalDesignDomainTests::test_the_boundary_is_derived_from_the_batch
- [ ] **AC2: the planner may add to it explicitly.**
  - **Given** a plan declaring an extra path the batch does not name
  - **When** the plan is written
  - **Then** the recorded boundary carries both the derived set and the addition, distinguishable from each other - D0239, so a wide boundary is visibly a choice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OperationalDesignDomainTests::test_an_authored_addition_is_recorded_and_distinguishable
- [ ] **AC3: the boundary records the budget the run may spend.**
  - **Given** a plan carrying an estimate
  - **When** the boundary is recorded
  - **Then** it carries that budget - a boundary that names files but not cost bounds nothing about how long the line may run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OperationalDesignDomainTests::test_the_budget_is_part_of_the_boundary
- [ ] **AC4: a batch declaring nothing does not yield an EMPTY boundary silently.**
  - **Given** a batch whose units carry no resolvable `Affects`
  - **When** the plan is written
  - **Then** it refuses rather than recording an empty domain - an empty boundary is not a tight one, it is one that permits nothing and would stop the line on its first edit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OperationalDesignDomainTests::test_an_underivable_boundary_is_refused_not_emptied

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, write the plan without recording any boundary, as it does today | the boundary is derived |
| AC2 | in `sprint.py`, merge an authored addition into the derived set so the two cannot be told apart | an addition stays distinguishable |
| AC3 | in `sprint.py`, record only the file set and drop the budget from the boundary | the budget is part of it |
| AC4 | in `sprint.py`, record an empty boundary when nothing resolves instead of refusing | an underivable boundary is refused |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
