# US0183: Record an operator Sprint Goal on plan and run-state; closing review verdict and sprint report display it

> **Status:** Draft
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0053
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** a one-line Sprint Goal recorded on the plan and judged at the closing review
**So that** a batch has a WHY, and the review can say whether the sprint achieved it

## Acceptance Criteria

### AC1: Goal recorded at plan time

- **Given** an operator planning a sprint
- **When** they supply --sprint-goal (or are prompted interactively)
- **Then** the goal sentence is recorded on the plan and run-state; absent, it records none - never invented
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_sprint.py -k SprintGoal

### AC2: Closing review judges the goal

- **Given** a run whose plan carries a goal
- **When** the mandatory closing review runs
- **Then** its verdict includes achieved/partial/missed with one line of judgement
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_sprint.py -k GoalVerdict

### AC3: Sprint report displays goal and verdict

- **Given** a closed sprint with a goal
- **When** sprint_report.py show renders
- **Then** the goal and the review's goal verdict appear beside delivered points and cost
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_sprint_report.py -k Goal

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
