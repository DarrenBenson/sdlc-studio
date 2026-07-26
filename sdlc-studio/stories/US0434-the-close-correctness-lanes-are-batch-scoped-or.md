# US0434: the close correctness lanes are batch-scoped, or --file-and-close files named out-of-batch debt

> **Status:** Draft
> **Delivers:** CR0421
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0162
> **Points:** 3

## User Story

**As an** operator closing a batch in a clean tree
**I want** the close's correctness lane to judge this batch's units, not the whole workspace
**So that** out-of-batch debt authored by someone else does not block an in-batch close - and when
debt does remain, `--file-and-close` files it by name rather than refusing outright

## Acceptance Criteria

### AC1: the close correctness lane is scoped to the batch

- **Given** an open run whose batch is fully delivered, and a clean tree containing an out-of-batch
  unit that fails conformance (a different epic, missing `verified` because its ACs are manual)
- **When** the close's correctness/conformance lane runs
- **Then** it judges only the batch's units and does not report the out-of-batch unit as a blocker -
  the whole-workspace scan no longer binds an in-batch close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::BatchScopedConformanceTests::test_close_conformance_lane_judges_only_the_batch

### AC2: file-and-close files named out-of-batch debt rather than refusing

- **Given** a close where the only remaining outstanding item is out-of-batch correctness debt
- **When** `sprint close --file-and-close --retro <id>` runs
- **Then** the debt is filed as a named unit recorded in the close, and the close proceeds - instead
  of being refused with "a correctness gate is red"
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseOutOfBatchTests::test_out_of_batch_correctness_debt_is_filed_not_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
