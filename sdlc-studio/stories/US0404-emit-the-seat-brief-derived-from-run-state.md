# US0404: emit the seat brief derived from run state, worklist, planner output and lessons, naming the grooming state

> **Status:** Draft
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Delivers:** CR0409
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0153
> **Points:** 5

## User Story

**As a** seat asked to review a Sprint Goal
**I want** a command that emits my brief for the current batch and goal, derived from the run state, the worklist and the planner's own output
**So that** the review's quality does not depend on how well the author I am meant to check chose to brief me

## Acceptance Criteria

### AC1: A command emits the seat brief, derived deterministically from the batch

- **Given** a planned batch and a stated goal
- **When** the seat brief is emitted
- **Then** it is composed from the run state, the worklist and the planner's output, and the same batch and goal produce the same brief every time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeatBriefEmitTests::test_the_brief_is_derived_deterministically_from_the_batch

### AC2: The brief names the batch's grooming state

- **Given** a batch whose stories carry placeholder acceptance criteria and whose planner derived shared-file clusters
- **When** the brief is emitted
- **Then** it names the placeholder acceptance criteria, the shared-file clusters and the reachable end state, the context the first live review turned on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeatBriefEmitTests::test_the_brief_names_placeholder_acs_shared_clusters_and_end_state

### AC3: The brief draws the project's relevant failure modes from the lessons registry

- **Given** a project lessons registry holding failure modes
- **When** the brief is emitted
- **Then** it includes the project's own relevant failure modes drawn from the registry, not a generic checklist
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeatBriefEmitTests::test_the_brief_draws_failure_modes_from_the_lessons_registry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
