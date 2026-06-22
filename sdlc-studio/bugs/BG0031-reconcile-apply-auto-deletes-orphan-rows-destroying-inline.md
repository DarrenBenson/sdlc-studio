# BG0031: reconcile apply auto-deletes orphan rows destroying inline-only records

> **Status:** Fixed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Severity:** High

## Summary

Concern from a consuming-project run: `--apply` would delete 'orphan' rows (inline-only bug records BG0081-0086). In current code `apply_type` already leaves structural classes (orphan/missing) report-only - but it was untested, so the guarantee could regress.

## Steps to Reproduce

Inline-only index rows (no backing file) reported as orphan-row; risk that a future apply removes them.

## Proposed Fix

Confirmed `apply_type` only rewrites status cells + counts (never deletes rows) and locked it with a regression test: an inline-only row survives apply unchanged.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
