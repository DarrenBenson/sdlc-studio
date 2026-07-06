# BG0053: artifact.py close records telemetry twice per close, inflating calibration data

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** High
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** S

## Summary

Every tool-driven close appends two `telemetry.jsonl` records for one close event.
`transition.transition` records on entering the terminal set (`transition.py:255-262`, with
no metrics because `artifact.close` does not pass them through), then `artifact.close`
unconditionally records again with metrics (`artifact.py:375-376`).

## Evidence

- `.claude/skills/sdlc-studio/scripts/transition.py:255-262` - records on ENTERING the
  terminal set ("one close (one event)").
- `.claude/skills/sdlc-studio/scripts/artifact.py:375-376` - `close()` calls
  `transition.transition(...)` then unconditionally `telemetry.record(...)` again.
- The unit test masks it: `scripts/tests/test_artifact.py:265-269` asserts only `recs[-1]`
  fields, never the record count.

## Impact

`telemetry show --summary` per-type counts, reopen-rate denominators, and verdict mixes are
inflated roughly 2x - corrupting exactly the estimation-calibration data the feature exists
to provide (README: "estimates calibrate against reality"). An idempotent re-close via
`close` appends a third record even though `transition` correctly suppresses it.

## Steps to Reproduce

1. `artifact.py new --type story ...`, then `artifact.py close <id> --force` with metrics.
2. Read `sdlc-studio/.local/telemetry.jsonl`: two records for the single close - one without
   metrics (from transition), one with (from close).

## Proposed Fix

In `artifact.close`, pass `metrics` into `transition.transition(..., metrics=metrics)` and
delete the second `telemetry.record` call. Add a regression test asserting exactly one
record per close (and none on idempotent re-close).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified at cited lines; filed from RV0006 architecture leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
