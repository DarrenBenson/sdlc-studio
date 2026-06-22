# CR-0076: CI coverage gate plus python security scan bandit (review WS B3c)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

World-class review WS B3c. CI runs lint + tests + a Windows smoke, but has no test-coverage signal and no Python security scan - both table-stakes for a world-class shared tool.

## Acceptance Criteria

- [x] `.github/workflows/lint.yml` gains a coverage step (report; threshold tuned to current) and a `bandit` Python security scan
- [x] the coverage + bandit steps are green on the current tree
- [x] documented in CONTRIBUTING (dev-workflow) if behaviour changes for contributors

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
