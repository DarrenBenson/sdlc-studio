# US0273: a standalone preflight reports every unmet close prerequisite in one read-only pass

> **Status:** Done
> **Delivers:** CR0359
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0089
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: every unmet prerequisite is reported in one pass, not one per run

- **Given** a workspace with SEVERAL unmet close prerequisites at once (say an unjudged sprint
  goal, a failing gate lane and unresolved drift)
- **When** `sprint.py preflight` runs
- **Then** all of them are listed together in a single invocation, because the information was
  always available before the first attempt and discovering it serially costs a full gate run per
  blocker
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_preflight_reports_every_blocker_in_one_pass
- **Verified:** yes (2026-07-20)

### AC2: the pre-flight is read-only

- **Given** a workspace with unmet prerequisites
- **When** the pre-flight runs
- **Then** the tree is byte-identical afterwards - it never scaffolds a retro, regenerates a
  summary or records a verdict, so it can be run to ask a question without committing to a close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_preflight_writes_nothing
- **Verified:** yes (2026-07-20)

### AC3: a clean workspace reports ready

- **Given** a workspace where every close prerequisite is met
- **When** the pre-flight runs
- **Then** it says so and exits 0, so "ready" is a positive answer rather than the absence of
  output
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_preflight_reports_ready_when_nothing_is_unmet
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
