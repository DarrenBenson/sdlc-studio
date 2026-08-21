# BG0601: The dry-run class sweep compares only the first two probes of each pair

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The parity sweep in `DryRunScratchParityTests` walks 22 probe classes and asserts the scratch and the read root agree, but it slices each probe's result to its first two elements before comparing. A probe whose divergence appears only from the third element on is reported as agreeing. The sweep was written to be the broad safety net under the read-root split, and a net with a two-element horizon is narrower than the thing it guards.

## Steps to Reproduce

In `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py`, find the class sweep in `DryRunScratchParityTests` and the `[:2]` slice applied to each probe's result. Construct a probe whose scratch and read-root results share their first two entries and differ at the third; the sweep passes. Removing the slice fails it. Demonstrated during BG0593's delivery, not hypothesised.

## Proposed Fix

Compare the probes in full, or state a bounded reason for the horizon in the test's own docstring so the next reader knows the sweep is partial. If a full comparison is too noisy, sort and compare as sets rather than truncating - truncation silently exempts the tail.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The parity sweep in `DryRunScratchParityTests` walks 22 probe classes and asserts the scratch and the read root agree, but it slices each probe's result to its...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In `.claude/skills/sdlc-studio/scripts/tests/test_sprint.py`, find the class sweep in `DryRunScratchParityTests` and the `[:2]` slice applied to each probe's...
- [ ] **AC3** The proposed fix lands, pinned by a test: Compare the probes in full, or state a bounded reason for the horizon in the test's own docstring so the next reader knows the sweep is partial.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Filed |
