# US0409: the choice is deterministic and the plan states the mode and why the alternative was or was not available

> **Status:** Review
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Delivers:** CR0411
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0154
> **Points:** 2

## User Story

**As a** reader of a sprint plan
**I want** the delivery-mode choice to be deterministic and the plan to state the mode used and why the alternative was or was not available
**So that** two runs of the same batch decide the mode the same way and anyone can see why parallel was or was not on offer

## Acceptance Criteria

### AC1: The offer is deterministic for a given batch and repo state

- **Given** the same batch and repo state
- **When** the delivery mode is determined twice
- **Then** the same modes are offered both times, computed from the shared-file clusters and dependency waves rather than from agent judgement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeDeterminismTests::test_the_same_batch_offers_the_same_modes_every_time

### AC2: The plan states the mode and why the alternative was or was not available

- **Given** a determined delivery mode
- **When** the plan is printed
- **Then** it states the mode and the reason the alternative was or was not available: one unit, one coupled cluster, or a dependency chain with no width
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DeliveryModeDeterminismTests::test_the_plan_states_the_mode_and_the_reason_for_the_alternative

## Verification depth

Node-addressed pytest ACs over `test_sprint.py`, red before the code (the offer, the test-file coupling and the determinism did not exist). Mutation-proven by hand (`__pycache__` purged, `python3 -B`): loosening the >=2 group threshold, dropping the Verify-derived files from coupling, inverting the record refusal, and removing the no-Affects safety branch were each caught by a node.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built: delivery-mode offer + test-file coupling + determinism, tested, mutation-proven |
