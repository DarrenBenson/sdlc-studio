# US1260: The bench runner passes a builder effort level to the harness CLI and records it on each run's result row

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0710
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/bench/runner.py, tools/tests/test_bench_effort_arm.py
> **Epic:** EP0350
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** The bench runner passes a builder effort level to the harness CLI and records it on each run's result row
**So that** CR0710 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: An effort level reaches the CLI and the result row

- **Given** a stand-in `claude` CLI on PATH that records its arguments and prints usage
- **When** `runner.py run` is run twice on one fixture and arm, once with `--effort low` and once without the flag
- **Then** the first session's command carries `--effort low` and its row records `effort` as `low`; the second session's command carries no effort flag and its row records no effort, not a default the runner made up. Fails on: a row that claims an effort the CLI was never given, or a flag passed and not recorded
- **Verify:** pytest tools/tests/test_bench_effort_arm.py::BenchEffortArmTests::test_effort_is_passed_to_the_cli_and_recorded_on_the_row

### AC2: A harness with no effort flag refuses the arm before a workspace is written

- **Given** a harness for which the runner holds no effort flag
- **When** `runner.py run --effort high` is run for it, and then the same run without `--effort`
- **Then** the first is refused naming the harness and the harnesses that take an effort level, with no workspace laid out and no row written; the second runs and records its row. Fails on: an effort arm run at the CLI's own default and recorded as `high`, which would make the two arms the same run
- **Verify:** pytest tools/tests/test_bench_effort_arm.py::BenchEffortArmTests::test_a_harness_without_an_effort_flag_refuses_the_arm

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
