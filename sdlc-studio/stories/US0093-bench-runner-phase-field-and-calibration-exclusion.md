# US0093: Bench runner: phase field and calibration exclusion

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0019
> **Persona:** Engineering seat
> **Affects:** tools/bench/runner.py, tools/tests/test_bench_runner.py

## User Story

**As an** operator producing a benchmark aggregate
**I want** calibration rows excluded from the summary by the tool, not by hand
**So that** protocol v2's no-pooling rule cannot be forgotten and silently pool calibration data into a published mean

Closes CR0196. Repo-only (`tools/bench/`, not in the skill payload). `protocol-v2.md` is frozen and unchanged.

## Acceptance Criteria

### AC1: record writes a phase field and existing rows are backfilled

- **Given** `runner.record`
- **When** a run is recorded without an explicit phase
- **Then** the entry carries `phase: "measured"` by default and accepts `phase: "calibration"`; existing `runs.jsonl` rows are backfilled (v2n1 rows = calibration, spike/measured rows = measured)
- **Verify:** pytest tools/tests/test_bench_runner.py::PhaseFieldTests

### AC2: summary excludes calibration rows unless explicitly included

- **Given** a results file mixing calibration and measured rows
- **When** `summary` runs without `--include-phase`
- **Then** calibration rows are excluded from every aggregate; `--include-phase calibration` opts them back in
- **Verify:** pytest tools/tests/test_bench_runner.py::SummaryPhaseTests

### AC3: a calibration row cannot move a measured aggregate

- **Given** a measured set and one extra calibration row for the same (fixture, arm)
- **When** the default summary is computed
- **Then** no measured mean/min/max/n changes versus the calibration row being absent
- **Verify:** pytest tools/tests/test_bench_runner.py::CalibrationIsolationTests

### AC4: the behaviour is documented and the protocol is unchanged

- **Given** the frozen `protocol-v2.md`
- **When** the feature ships
- **Then** the runner help text describes `--include-phase` and the default exclusion; `protocol-v2.md` is byte-unchanged
- **Verify:** shell python3 tools/bench/runner.py summary -h 2>&1 | grep -q include-phase

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0196 |
