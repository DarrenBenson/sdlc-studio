# US0229: record a standing sprint policy (N cycles, goal/capacity/order/stop conditions) on run-state

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0076
> **Points:** 3

## User Story

**As an** operator running an unattended evening of delivery
**I want** to fix the sprint policy once - cycle count, goal, capacity, order, stop conditions - and have it recorded on run-state
**So that** every later cycle plans under the rule I approved rather than under whatever the CLI defaults to

## Acceptance Criteria

### AC1: Accept and record the standing policy

- **Given** a repo with a backlog and no open run
- **When** the operator runs `sprint.py plan --write` with `--cycles N` plus the policy elements (sprint goal, appetite, order, stop conditions)
- **Then** run-state carries a `policy` object holding the cycle count, goal, capacity, order rule and stop conditions, and the plan output echoes the policy it recorded
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k RollingPolicyRecordTests

### AC2: Refuse an incomplete policy rather than default it

- **Given** `--cycles` passed with a value below 1, or without a sprint goal
- **When** `plan --write` runs
- **Then** it refuses with exit 2 naming the missing or invalid element, and no policy is written to run-state
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k RollingPolicyRefusalTests

### AC3: The policy carries across a boundary unchanged

- **Given** a run-state carrying a rolling policy whose first cycle has closed
- **When** the next cycle opens
- **Then** it reads the recorded policy (goal, capacity, order, stop conditions) rather than re-deriving it from CLI defaults, and the remaining-cycle count decrements by one
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k RollingPolicyCarryOverTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
