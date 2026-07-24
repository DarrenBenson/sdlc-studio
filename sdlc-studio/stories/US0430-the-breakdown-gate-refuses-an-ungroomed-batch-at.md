# US0430: the breakdown gate refuses an ungroomed batch at --goal done and accepts it at --goal design

> **Status:** Review
> **Delivers:** CR0418
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0160
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: an ungroomed batch is refused at --goal done

- **Given** a batch containing a story with placeholder acceptance criteria
- **When** `sprint plan --goal done` runs
- **Then** it is REFUSED and names the ungroomed units - this is today's behaviour and must not weaken; D0062 narrows the gate, it does not remove it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalAwareBreakdownTests::test_an_ungroomed_batch_is_still_refused_at_goal_done
- **Verified:** yes (2026-07-24)

### AC2: the same batch is accepted at --goal design

- **Given** that same batch
- **When** `sprint plan --goal design` runs
- **Then** it is ACCEPTED - the design rung exists to produce the grooming, and refusing it for the absence of what it produces is the circularity CR0418 recorded
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalAwareBreakdownTests::test_the_same_batch_is_accepted_at_goal_design
- **Verified:** yes (2026-07-24)

### AC3: Affects and the split ceiling still bind at every rung

- **Given** a batch with a unit over the point ceiling, or one declaring no files
- **When** the plan runs at `--goal design`
- **Then** it is still refused - D0062 exempts ungroomed ACs only. A unit nobody can size or place is unplannable at any rung
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalAwareBreakdownTests::test_the_size_and_affects_gates_bind_at_the_design_rung_too
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
