# BG0363: gate.py records a cost baseline on every CLI run including scoped ones, so the trend compares unlike runs

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

The baseline is written whenever the CLI runs, including `--only` and `--skip` invocations that cover a fraction of the lanes. A scoped run therefore lowers the recorded baseline, and the next full run reads as a regression against a number that never measured the same thing.

## Steps to Reproduce

Reported by a delivery lane during RUN-01KYKVZM; see the summary for the measurement.

## Proposed Fix

See the summary; the remedy is stated with the defect.

## Acceptance Criteria

### AC1: a scoped run does not write the baseline

- **Given** a `--only` or `--skip` run against a recorded full-run baseline
- **When** it runs
- **Then** the baseline is unchanged, so a scoped run cannot lower the number the next full run is judged against
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ScopedRunIsNotABaselineTests::test_a_scoped_run_does_not_write_the_baseline
- **Verified:** yes (2026-07-29)

### AC2: `--skip` narrows the run exactly as `--only` does

- **Given** a `--skip` run
- **When** it runs
- **Then** the baseline is unchanged too, because a fix covering one spelling is the enumerated-list shape this repo's carried lessons already name
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ScopedRunIsNotABaselineTests::test_a_skipped_run_does_not_write_the_baseline_either
- **Verified:** yes (2026-07-29)

### AC3: a full run still writes it

- **Given** an unscoped run
- **When** it runs
- **Then** the baseline is updated, because a baseline nothing writes is a baseline nobody has
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ScopedRunIsNotABaselineTests::test_a_full_run_still_writes_it
- **Verified:** yes (2026-07-29)

### AC4: a scoped run is not compared with the baseline either, and says so

- **Given** a scoped run reporting its cost
- **When** it runs
- **Then** no faster/slower comparison is printed and the report states it is scoped - a fraction of the lanes measured against a full baseline reports a saving nobody made, and it looks like good news
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ScopedRunIsNotABaselineTests::test_a_scoped_run_is_not_compared_with_the_baseline_and_says_so
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
