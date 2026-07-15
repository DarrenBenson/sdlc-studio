# US0159: A cost-estimate helper: agents, tokens and wall-time for a scoped audit run

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/audit_cost.py
> **Epic:** EP0044
> **Points:** 3

## User Story

**As** the audit command
**I want** to estimate a run's cost before fanning out
**So that** a large run can be flagged and confirmed, not sprung on the operator.

## Acceptance Criteria

### AC1: the estimate matches the reference run and flags large vs small

- **Given** a lens count (and rounds/votes)
- **When** `audit_cost.estimate()` runs
- **Then** the 7-lens estimate lands near the measured reference (150-230 agents, 5-9M tokens, 20-50 min) and is flagged large; a small scoped audit is not large; the breakdown adds up
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_audit_cost
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
