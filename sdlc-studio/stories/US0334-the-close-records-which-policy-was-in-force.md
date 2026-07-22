# US0334: The close records which policy was in force and lists the findings carried, so a converged sprint is distinguishable from one that carried findings

> **Status:** Draft
> **Delivers:** CR0404
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0113
> **Points:** 3

## User Story

**As a** reader of a closed sprint
**I want** the close to say which policy was in force and what it carried
**So that** a sprint that converged is distinguishable from one that shipped with findings
open, months later and without asking anyone

## Acceptance Criteria

### AC1: the close records the policy that was actually in force

- **Given** a sprint closed under carry-forward
- **When** the run state is written
- **Then** it records the policy resolved at close time, not the one configured when the run
  opened, because a policy changed mid-run would otherwise be reported as the one that
  governed decisions it never governed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CarryForwardCloseTests::test_the_close_records_the_policy_resolved_at_close_time

### AC2: the carried findings are listed, and an empty list is distinguishable from none

- **Given** two closes under carry-forward, one carrying two findings and one carrying none
- **When** each is rendered
- **Then** the first lists both by id and the second says plainly that nothing was carried,
  so a reader can tell a clean close from one whose list was dropped
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CarryForwardCloseTests::test_a_close_carrying_nothing_is_distinguishable_from_a_dropped_list

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
