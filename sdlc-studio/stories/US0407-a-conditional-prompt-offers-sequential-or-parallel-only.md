# US0407: a conditional prompt offers SEQUENTIAL or PARALLEL only when a genuine file-disjoint decomposition exists, and records the chosen mode

> **Status:** Draft
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-delivery.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Delivers:** CR0411
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0154
> **Points:** 5

## User Story

**As a** operator starting a sprint run
**I want** to be asked for SEQUENTIAL or PARALLEL delivery, but only when the batch has a genuine file-disjoint decomposition
**So that** the delivery mode is my deterministic choice and I am never offered a parallel path that would only conflict on merge

## Acceptance Criteria

### AC1: A parallelisable batch offers both modes and records the choice

- **Given** a batch of more than one unit with at least two clusters whose file sets are disjoint and whose dependency waves permit concurrency
- **When** sprint plan runs at run start
- **Then** it offers SEQUENTIAL or PARALLEL and records the chosen mode on the run state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeOfferTests::test_a_parallelisable_batch_offers_both_modes_and_records_the_choice

### AC2: A one-unit batch is delivered sequentially and says why parallel was withheld

- **Given** a batch of a single unit
- **When** sprint plan runs
- **Then** parallel is not offered, the run is sequential, and the output states parallel was withheld because there is only one unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeOfferTests::test_a_one_unit_batch_is_sequential_and_says_why_parallel_was_withheld

### AC3: An all-coupled batch is not offered parallel

- **Given** a batch whose units all touch one shared file, forming a single coupled cluster
- **When** sprint plan runs
- **Then** parallel is not offered and the stated reason names the coupling
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeOfferTests::test_an_all_coupled_batch_is_not_offered_parallel

## Verification depth

Node-addressed pytest ACs over `test_sprint.py`, red before the code (the offer, the test-file coupling and the determinism did not exist). Mutation-proven by hand (`__pycache__` purged, `python3 -B`): loosening the >=2 group threshold, dropping the Verify-derived files from coupling, inverting the record refusal, and removing the no-Affects safety branch were each caught by a node.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built: delivery-mode offer + test-file coupling + determinism, tested, mutation-proven |
