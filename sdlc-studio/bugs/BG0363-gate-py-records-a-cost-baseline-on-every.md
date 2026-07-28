# BG0363: gate.py records a cost baseline on every CLI run including scoped ones, so the trend compares unlike runs

> **Status:** Open
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM delivery lanes, dogfooding friction) | Filed |
