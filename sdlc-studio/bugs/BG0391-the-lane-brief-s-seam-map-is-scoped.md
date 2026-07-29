# BG0391: The lane brief's seam map is scoped to the invocation, so the documented one-unit dispatch never shows a seam

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
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

### AC1: a single-unit brief names its seams with the OPEN RUN's batch

- **Given** an open run of two units sharing a file, and `lane brief --units US0002`
- **When** it runs
- **Then** the brief carries the seam with US0001, which a map scoped to the invocation could never find - and one-unit dispatch is the documented way lanes are briefed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneSeamScopeTests::test_a_single_unit_brief_names_its_seams_with_the_open_batch
- **Verified:** yes (2026-07-29)

### AC2: the brief still carries only its own seams

- **Given** a unit sharing no file with the batch
- **When** it runs
- **Then** it is handed no pair, so widening the SCOPE does not widen the brief into noise a lane skips
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneSeamScopeTests::test_the_brief_still_carries_only_its_own_seams
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
