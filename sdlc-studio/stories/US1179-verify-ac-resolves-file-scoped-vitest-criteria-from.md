# US1179: verify_ac resolves file-scoped vitest criteria from one batched vitest JSON run, with vitest stubbed in the test

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0638
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_batch.py
> **Epic:** EP0319
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** verify_ac resolves file-scoped vitest criteria from one batched vitest JSON run, with vitest stubbed in the test
**So that** CR0638 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Fifty file-scoped vitest criteria resolve from one run

- **Given** a fixture project with fifty criteria written `shell npx vitest run <file> -t "<name>"` across several test files, and a stub `npx` on PATH that logs each call and prints vitest's JSON reporter output for those files
- **When** `verify_ac.py run` walks the stories with batching on
- **Then** the stub's call log holds exactly one vitest invocation, every one of the fifty criteria is resolved from it with the pass or fail its JSON assertion carries, and stderr says how many assertions the one run cached. Fails on: one vitest start per criterion, which is the path the tree has today
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_batch.py::VitestBatchTests::test_fifty_criteria_resolve_from_one_run

### AC2: A failed, skipped or todo assertion in the batch is never read as a pass

- **Given** a batch whose JSON holds one failed assertion, one skipped and one todo beside the passing ones
- **When** the criteria naming them are resolved from the cache
- **Then** the failed one is red and the skipped and todo ones are not green: each reads as a per-criterion run of the same test reads it. Fails on: a cache that answers green for any assertion it holds a record of
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_batch.py::VitestBatchTests::test_a_failed_or_skipped_assertion_is_not_a_pass

### AC3: What the batch cannot answer is left unresolved for the caller

- **Given** a criterion whose file or test name is absent from the batch's JSON, a criterion with no file in its command, and a batch run that exits without parseable JSON or times out
- **When** each is looked up in the cache
- **Then** none is resolved from it: the absent and the file-less criterion return no cached answer while their neighbours still do, and the failed batch yields an empty cache, so every criterion falls to its own subprocess. Fails on: an absent test reported green by a batch that ran nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_vitest_batch.py::VitestBatchTests::test_an_absent_test_or_a_failed_batch_resolves_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
