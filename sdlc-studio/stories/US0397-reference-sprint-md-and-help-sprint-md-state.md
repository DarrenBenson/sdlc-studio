# US0397: reference-sprint.md and help/sprint.md state the fixed-cost-versus-review-convergence trade-off from the measured rows, prescribing no number

> **Status:** Done
> **Delivers:** CR0398
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0149
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: The sprint guidance states the trade-off: fixed cost falls per point as the batch grows, review

- **Given** the trade-off paragraph in reference-sprint.md and help/sprint.md
- **When** both arms are read
- **Then** The sprint guidance states the trade-off: fixed cost falls per point as the batch grows, review convergence cost rises with it.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::BatchSizeTradeoffDocTests::test_it_states_both_arms_of_the_trade_off .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::HelpStatesBatchSizeTradeoffTests::test_it_states_the_trade_off_grounds_it_and_prescribes_no_number
- **Verified:** yes (2026-07-24)

### AC2: It is grounded in this project's own measured rows and names how many sprints it rests on

- **Given** the trade-off paragraph
- **When** its evidence basis is read
- **Then** It is grounded in this project's own measured rows and names how many sprints it rests on.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::BatchSizeTradeoffDocTests::test_it_is_grounded_in_measured_rows_and_names_how_many_sprints
- **Verified:** yes (2026-07-24)

### AC3: It prescribes NO number: with few measured sprints there is no defensible optimum, and inventing

- **Given** the trade-off paragraph
- **When** it is read for a prescribed batch size
- **Then** It prescribes NO number: with few measured sprints there is no defensible optimum, and inventing one repeats the mistake this project has twice had to undo.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::BatchSizeTradeoffDocTests::test_it_prescribes_no_number
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
