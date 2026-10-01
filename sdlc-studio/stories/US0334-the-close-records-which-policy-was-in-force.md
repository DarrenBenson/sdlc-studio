# US0334: The close records which policy was in force and lists the findings carried, so a converged sprint is distinguishable from one that carried findings

> **Status:** Done
> **Verification depth:** functional - node-addressed tests in test_critic/test_conformance/test_sprint, all green; carry_forward mutation-proven (7 mutants killed incl. a non-resolving ref)
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
- **Verify:** manual - retired by BG0831: the carry-forward review policy and its key `review.policy` were deleted: every project carries a unit whose REJECT stands at the round cap (`review.max_rounds`), filing its findings
- **Verified:** manual (2026-10-01) - retired, superseded by BG0831

### AC2: the carried findings are listed, and an empty list is distinguishable from none

- **Given** two closes under carry-forward, one carrying two findings and one carrying none
- **When** each is rendered
- **Then** the first lists both by id and the second says plainly that nothing was carried,
  so a reader can tell a clean close from one whose list was dropped
- **Verify:** manual - retired by BG0831: the carry-forward review policy and its key `review.policy` were deleted: every project carries a unit whose REJECT stands at the round cap (`review.max_rounds`), filing its findings
- **Verified:** manual (2026-10-01) - retired, superseded by BG0831

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
