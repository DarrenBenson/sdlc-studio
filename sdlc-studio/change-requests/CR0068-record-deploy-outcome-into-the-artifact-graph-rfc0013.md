# CR-0068: record deploy outcome into the artifact graph (RFC0013 WS3)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

RFC0013 WS3. Close the loop: `deploy.py record` appends the deploy outcome (rolled-out / verified / rolled-back / failed) to `sdlc-studio/deploy-log.md`, feeding the last mile back into the artifact graph.

## Acceptance Criteria

- [x] `deploy.py record --status <s> --detail` appends a timestamped, table-safe row to `sdlc-studio/deploy-log.md`
- [x] status is constrained to the four outcomes; unknown status errors
- [x] the log is created with a header on first write, append-only after; tests cover append/reject/sanitise/single-header

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
