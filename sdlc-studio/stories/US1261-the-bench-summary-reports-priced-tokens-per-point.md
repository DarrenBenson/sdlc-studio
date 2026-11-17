# US1261: The bench summary reports priced tokens per point, review rounds, rejections and the held-back score for each effort arm

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0710
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/bench/runner.py, tools/tests/test_bench_effort_summary.py
> **Epic:** EP0350
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** The bench summary reports priced tokens per point, review rounds, rejections and the held-back score for each effort arm
**So that** CR0710 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each effort arm is summarised on its own

- **Given** a results log holding measured rows for one fixture, arm and harness at two effort levels, each row carrying its points, review rounds, rejections and held-back result, and one older row that names no effort
- **When** `runner.py summary` is run
- **Then** the two effort levels are separate groups, each stating its effort, mean priced tokens per point, mean review rounds, rejections and held-back pass rate, and the row naming no effort keeps the group key it has today. Fails on: rows of two effort levels pooled into one mean, or an older log whose keys change
- **Verify:** pytest tools/tests/test_bench_effort_summary.py::BenchEffortSummaryTests::test_each_effort_arm_reports_cost_per_point_rounds_rejections_and_score

### AC2: A figure no row can supply reads as absent, never zero

- **Given** a group whose rows carry no points, and a group whose rows carry no review rounds or rejections
- **When** `runner.py summary` is run
- **Then** the first group's priced tokens per point is null with the reason that its rows name no points, and the second group's review rounds and rejections are null; a group with a genuine zero rejections reads 0. Fails on: a missing count printed as 0, which would read as an arm that was never rejected
- **Verify:** pytest tools/tests/test_bench_effort_summary.py::BenchEffortSummaryTests::test_an_absent_figure_is_null_and_a_real_zero_is_zero

### AC3: A run records what the summary needs from the finished workspace

- **Given** a finished workspace whose review ledger holds two rounds on one unit, one of them a rejection, and a second workspace that holds no review ledger
- **When** `runner.py run` records each
- **Then** the first row carries the fixture's points, 2 review rounds and 1 rejection read from that ledger; the second row carries no review rounds or rejections. Fails on: counts typed by hand that the workspace does not hold, or an arm with no ledger recorded as zero rounds
- **Verify:** pytest tools/tests/test_bench_effort_summary.py::BenchEffortSummaryTests::test_a_run_reads_rounds_and_rejections_from_the_workspace_ledger

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
