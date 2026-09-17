# US0843: module-alone prints the per-module wall clock it already computes, so a narrowing can be judged before it is built

> **Status:** Draft
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0253
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** operator deciding whether to fund a narrowing
**I want** the per-module timings the lane already computes to be printed and recorded, split by phase
**So that** a fourteen-point change is judged on its measured saving rather than on an assumption about where the time goes

## Acceptance Criteria

The lane already measures every module: `run()` returns elapsed seconds as its fourth value and the summary discards it (`for mod, rc, out, _secs in results`, gate.py:1231). This story spends nothing measuring and only stops throwing the measurement away. It ships BEFORE US0824 under D0211, because the narrowing's value cannot be judged without it.

### AC1: the lane's own line names its slowest modules with their wall clock

- **Given** a `gate.py --boundary push` run over this repository's 133 test modules
- **When** the module-alone lane reports
- **Then** its detail names the three slowest modules with their durations to the nearest second, longest first, beside the existing module and worker counts
- **Mutant:** keep `_secs` discarded and print the counts alone - the line reads exactly as it does today and the lane looks measured when it is not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneTimingTests::test_the_lane_line_names_its_slowest_modules_with_their_seconds

### AC2: the phase figures are reported separately, because only one of them a narrowing can move

- **Given** the same run, whose parallel phase is bounded by its slowest member and whose serial phase runs after it
- **When** the lane reports
- **Then** the detail carries the parallel phase's wall clock and the serial phase's wall clock as two figures, never one total, and names the serial modules
- **Mutant:** report the SUM of the module durations as the lane's cost - it implies a saving from narrowing the selection that a 16-way parallel phase cannot deliver, which is the reading that put a 14-point epic in front of the operator
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneTimingTests::test_parallel_and_serial_phases_are_reported_as_two_figures

### AC3: the timings are recorded where a later run can compare them

- **Given** a completed module-alone lane
- **When** it finishes
- **Then** it writes each module's duration and phase to `sdlc-studio/.local/module-alone-timings.json` with the run's boundary and a timestamp, and a second run overwrites rather than appends
- **Mutant:** write the total only - a before-and-after comparison then needs the logs, which is how this lane's cost went unmeasured through eleven sprints
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneTimingTests::test_per_module_timings_are_written_for_comparison

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
