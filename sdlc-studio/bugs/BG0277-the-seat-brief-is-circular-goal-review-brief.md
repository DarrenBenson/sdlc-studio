# BG0277: the seat brief is circular: goal-review brief derives from the persisted sprint-plan.json, but the goal review it informs gates plan --write, so on a new sprint the brief silently describes the PREVIOUS batch

> **Status:** Fixed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Verification depth:** functional (unit: the seat brief derives from the worklist it is given rather than the persisted plan, and a stale persisted plan is detected)
> **Severity:** Medium
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit live opening Sprint 2, dogfooding the seat brief shipped last sprint (US0404/US0405).

The ordering is circular:

1. `sprint plan --write` REFUSES a stated Sprint Goal no seat has reviewed, on a project that
   declares review seats. So the goal review must happen FIRST.
2. `goal-review brief` composes the brief from `sdlc-studio/.local/sprint-plan.json` - the
   PERSISTED plan.
3. A dry `sprint plan` (no `--write`) does not refresh that file. Measured: after planning the
   27-unit Sprint 2 batch, `sprint-plan.json` still read `count: 19, first: US0371` - Sprint 1.

So the brief a seat is given before reviewing Sprint 2's goal described Sprint 1's batch: its unit
count, its clusters, its reachable end state. Nothing warns. The seat is briefed on the wrong
sprint and cannot tell.

This defeats the point of US0405 ("a thin verdict can be told from a thin brief") - the brief is
not thin, it is CONFIDENTLY WRONG, which is the failure mode this project ranks worse.

## Acceptance Criteria

- [ ] AC1: the brief describes the batch being reviewed, not the last one planned
- **Given** a goal review for a batch that has not yet been written to the plan file
- **When** `goal-review brief` runs for that batch
- **Then** it describes THAT batch - by taking the worklist/query it is to brief, or by composing from a dry plan of it - never a stale persisted plan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeatBriefFreshnessTests::test_the_brief_describes_the_batch_it_is_given_not_the_persisted_plan

- [ ] AC2: a brief with no batch to describe says so rather than describing an old one
- **Given** no batch is supplied and the persisted plan belongs to a different, closed run
- **When** the brief is composed
- **Then** it states plainly that it has no current batch, instead of silently rendering the previous run's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeatBriefFreshnessTests::test_a_stale_plan_is_named_not_rendered_as_current

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Fixed and mutation-proven |
