# BG0391: The lane brief's seam map is scoped to the invocation, so the documented one-unit dispatch never shows a seam

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`lane_dispatch` computes seams over the ids passed to THAT call. The shipped docs dispatch one unit at a time (`lane brief --units <id>`), so the feature works only when the whole batch is briefed in one command - which is the case where a lane is not the one-unit reader the design is premised on.

## Steps to Reproduce

Open a run with two units sharing a file; `lane brief --units US0002` prints no seam line, `lane brief` with no --units prints one.

## Proposed Fix

Compute seams against the open run's approved batch, then filter to the briefed unit.

## Acceptance Criteria

- [ ] A single-unit brief names the seams that unit has with the rest of the OPEN RUN's batch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
