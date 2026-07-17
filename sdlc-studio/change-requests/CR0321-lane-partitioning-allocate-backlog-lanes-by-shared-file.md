# CR-0321: Lane partitioning: allocate backlog lanes by shared-file cluster for multi-team delivery (RFC0036 follow-up)

> **Status:** Deferred
> **Parent:** RFC0036
> **Priority:** Low
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; RFC triage decisions, filed by Claude Fable 5

## Summary

RFC0036's second half, deliberately deferred behind the rolling policy (operator scoping): partition a batch into lanes with no file in common using the existing Affects-derived cluster computation, so lanes cannot collide by construction and can be handed to different teams, agents or worktrees. Report-only first; allocation/export second.

## Impact

Two teams or agents on one backlog rely on luck not to collide; the shared-file cluster computation that already warns about false-parallel waves could mechanically allocate collision-free lanes.

## Acceptance Criteria

- [ ] sprint plan can emit a lane partition (clusters sharing no files) for a batch, report-only
- [ ] A lane exports as a per-team worklist file; collision-freedom is asserted from declared Affects with the undeclared-file risk stated

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson | Raised |
