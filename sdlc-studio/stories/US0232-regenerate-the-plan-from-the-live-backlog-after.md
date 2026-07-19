# US0232: regenerate the plan from the live backlog after the fetch; dry-run preview before continuing

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0076
> **Points:** 5

## User Story

**As an** operator running several cycles under one policy
**I want** each cycle's batch computed fresh from the backlog as it actually is at that boundary
**So that** findings and lessons raised by the previous cycle can enter the next one instead of rotting outside a frozen queue

## Acceptance Criteria

### AC1: Select the next batch from the live backlog

- **Given** a cycle that raised a new bug and completed one of its stories
- **When** the next cycle plans under the standing policy
- **Then** its batch is selected afresh under the policy's status filters and order rule, containing the newly raised unit and excluding the completed one - no batch is carried over from the previous cycle
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k RegeneratedBatchFromLiveBacklogTests

### AC2: Absorb the previous cycle's lessons

- **Given** a cycle whose close wrote new lessons entries
- **When** the next cycle's plan is regenerated
- **Then** that plan's lessons digest includes those entries, so each cycle plans having read the one before it
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k RegeneratedPlanLessonsTests

### AC3: Preview the regenerated plan before continuing

- **Given** a boundary that has passed the close-down chain and the drift check
- **When** the next cycle's plan is regenerated
- **Then** a dry-run preview of that plan - batch, order, forecast and capacity - is printed before the cycle executes
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k NextCyclePreviewTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
