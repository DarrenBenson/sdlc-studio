# US0170: Triage pass inside sprint plan: oversized blocks, judgement lenses report, drops logged

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0047
> **Points:** 5

## User Story

**As an** operator reading a sprint plan
**I want** the judgement triage findings shown in the plan
**So that** a dirty backlog is seen before it is planned FROM, not after

## Acceptance Criteria

### AC1: a batch containing a duplicate surfaces a triage section in the plan and still plans (reporting, not a refusal)

- **Given** a batch of two groomed bugs that are a duplicate pair
- **When** `sprint plan` runs
- **Then** the plan prints and a `backlog triage` section names the duplicate; the plan is not refused
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py -k TriageInPlan
- **Verified:** yes (2026-07-16)

### AC2: a coherent batch prints no triage section

- **Given** a batch with no triage findings
- **When** `sprint plan` runs
- **Then** no `backlog triage` section appears
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py -k TriageInPlan
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
