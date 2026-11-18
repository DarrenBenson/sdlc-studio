# US1180: The release verify lane reads the vitest batch, falls back per criterion where it cannot answer, and the two agree

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0638
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/tests/test_gate_vitest_batch.py
> **Epic:** EP0319
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The release verify lane reads the vitest batch, falls back per criterion where it cannot answer, and the two agree
**So that** CR0638 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The release verify lane spends one vitest run on the criteria the batch answers

- **Given** a vitest fixture project (a stub `npx` logging its calls) whose stories carry file-scoped vitest criteria
- **When** `gate.py --release` runs its verify lane
- **Then** the stub's log holds one batched vitest run and no per-criterion run for any criterion the batch answered, and the lane's verdict counts those criteria as executed. Fails on: the lane spawning vitest once per criterion, the 1,800 s path CR0638 measured
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_vitest_batch.py::GateVitestBatchTests::test_the_release_lane_runs_vitest_once_for_what_the_batch_answers

### AC2: A criterion the batch cannot answer runs its own subprocess

- **Given** the same project with one criterion naming a test the batch's JSON does not hold, and a second pass in which the batch run itself fails
- **When** the verify lane runs
- **Then** in the first pass exactly that criterion is run on its own and the rest come from the batch; in the second every vitest criterion is run on its own, and a red one is still reported red. Fails on: an unanswered criterion counted green or skipped, or a failed batch turning the lane green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_vitest_batch.py::GateVitestBatchTests::test_an_unanswered_criterion_falls_back_to_its_own_run

### AC3: The batch and the per-criterion path give the same verdict over a fixture corpus

- **Given** a fixture corpus holding a passing, a failing, a skipped and a missing vitest criterion
- **When** the verify lane judges it once with the batch and once with batching off
- **Then** both runs report the same red criterion ids and the same executed, red and unbuilt counts. Fails on: a criterion whose verdict depends on which path resolved it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_vitest_batch.py::GateVitestBatchTests::test_the_batch_and_the_per_criterion_verdicts_agree

### AC4: The gate help says the verify lane batches vitest

- **Given** `help/gate.md`'s account of the release verify lane
- **When** a reader of a vitest project looks up why the lane is slow
- **Then** it says file-scoped vitest criteria are resolved from one batched run with a per-criterion fallback, and names the criterion form the batch reads. Fails on: a help page that still names only the jest and pytest batches
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_vitest_batch.py::GateVitestBatchTests::test_the_gate_help_names_the_vitest_batch

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
